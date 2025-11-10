"""
Strategy Pattern Implementation for LLM Providers

This module implements the Strategy design pattern to handle different LLM providers
(Gemini, OpenAI, Local) with a common interface. This allows for easy switching between
providers and adding new ones without modifying existing code.

Benefits:
- Open/Closed Principle: Easy to add new providers
- Single Responsibility: Each provider encapsulates its own logic
- Testability: Easy to mock and test individual providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import requests
import re
import json
from config import settings


class LLMResponse:
    """Data class for LLM responses"""
    def __init__(self, text: str, tokens_used: int, model: str, provider: str):
        self.text = text
        self.tokens_used = tokens_used
        self.model = model
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "tokens_used": self.tokens_used,
            "model": self.model,
            "provider": self.provider
        }


class LLMStrategy(ABC):
    """
    Abstract base class for LLM provider strategies.

    This defines the interface that all LLM providers must implement.
    Following the Strategy pattern, each concrete implementation encapsulates
    its own algorithm for generating responses.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int,
        timeout: int = 60,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts

        Returns:
            LLMResponse object containing the generated text and metadata
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of this provider"""
        pass


class GeminiStrategy(LLMStrategy):
    """
    Concrete strategy for Google Gemini API.

    Implements the LLM generation using Gemini's REST API with proper
    safety settings for academic content.
    """

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    def get_provider_name(self) -> str:
        return "gemini"

    def generate(
        self,
        prompt: str,
        max_tokens: int,
        timeout: int = 60,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Generate response using Gemini REST API with retry logic and rate limiting.
        """
        for attempt in range(max_retries):
            try:
                return self._make_api_call(prompt, max_tokens, timeout)

            except Exception as e:
                error_str = str(e).lower()
                original_error = str(e)

                # Handle timeout errors
                if self._is_timeout_error(error_str):
                    if attempt < max_retries - 1:
                        timeout, wait_time = self._handle_timeout_retry(timeout, attempt)
                        time.sleep(wait_time)
                        continue
                    raise Exception(f"Gemini API request timed out after {max_retries} retries. Error: {str(e)}")

                # Handle rate limiting (429 errors)
                if self._is_rate_limit_error(error_str):
                    if attempt < max_retries - 1:
                        retry_delay = self._calculate_rate_limit_delay(original_error)
                        print(f"Rate limit hit, waiting {retry_delay:.1f} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"Gemini API rate limit exceeded after {max_retries} retries. Error: {str(e)}")

                # Handle token limit errors
                if self._is_token_limit_error(error_str):
                    if attempt < max_retries - 1:
                        prompt, max_tokens = self._handle_token_limit(prompt, max_tokens, attempt)
                        time.sleep(1)
                        continue

                # For other errors, retry with exponential backoff
                if attempt < max_retries - 1 and not self._is_blocking_error(error_str):
                    time.sleep(2 ** attempt)
                    continue

                raise Exception(f"Gemini API error: {str(e)}")

        raise Exception(f"Gemini API failed after {max_retries} attempts")

    def _make_api_call(self, prompt: str, max_tokens: int, timeout: int) -> LLMResponse:
        """Make the actual API call to Gemini REST API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Safety settings for academic content (BLOCK_NONE)
        safety_settings = [
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        # Calculate effective max tokens based on prompt length
        effective_max_tokens = self._calculate_effective_max_tokens(prompt, max_tokens)

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": effective_max_tokens,
                "temperature": 1.0
            },
            "safetySettings": safety_settings
        }

        response = requests.post(url, headers=headers, json=payload, timeout=timeout)

        if response.status_code != 200:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get("error", {}).get("message", str(response.status_code))
            raise Exception(f"Gemini API HTTP error {response.status_code}: {error_msg}")

        data = response.json()

        # Validate and extract response
        return self._parse_response(data)

    def _calculate_effective_max_tokens(self, prompt: str, max_tokens: int) -> int:
        """Calculate effective max tokens based on prompt length"""
        prompt_token_estimate = len(prompt) // 4
        MAX_CONTEXT_TOKENS = 1000000
        SAFE_BUFFER = 50000
        MIN_OUTPUT_TOKENS = 500

        available_for_output = MAX_CONTEXT_TOKENS - prompt_token_estimate - SAFE_BUFFER
        effective_max_tokens = min(
            max_tokens,
            max(MIN_OUTPUT_TOKENS, available_for_output),
            55000  # Hard cap for Gemini models
        )

        if available_for_output < MIN_OUTPUT_TOKENS:
            print(f"WARNING: Prompt is very long. Setting maxOutputTokens to minimum {MIN_OUTPUT_TOKENS}.")
        elif effective_max_tokens < max_tokens:
            print(f"WARNING: Reducing maxOutputTokens from {max_tokens} to {effective_max_tokens} to fit context.")

        return effective_max_tokens

    def _parse_response(self, data: Dict[str, Any]) -> LLMResponse:
        """Parse and validate Gemini API response"""
        if "error" in data:
            error_info = data["error"]
            raise Exception(f"Gemini API error: {error_info.get('message', 'Unknown error')}")

        if "candidates" not in data or not data["candidates"]:
            if "promptFeedback" in data:
                feedback = data["promptFeedback"]
                block_reason = feedback.get("blockReason")
                if block_reason:
                    raise Exception(f"Gemini API blocked prompt: {block_reason}")
            raise Exception("No candidates in API response")

        candidate = data["candidates"][0]
        finish_reason = candidate.get("finishReason")

        # MAX_TOKENS is acceptable (response was truncated but valid)
        if finish_reason and finish_reason not in ["STOP", "MAX_TOKENS"]:
            raise Exception(f"API blocked: finishReason={finish_reason}")

        if "content" not in candidate or "parts" not in candidate["content"]:
            if finish_reason == "MAX_TOKENS":
                raise ValueError("TOKEN_LIMIT_NO_CONTENT: Prompt too long")
            raise Exception("No content in response")

        text = candidate["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        tokens_used = usage.get("totalTokenCount", 0)

        if finish_reason == "MAX_TOKENS":
            print(f"Response truncated at token limit (acceptable)")

        return LLMResponse(text, tokens_used, self.model, "gemini")

    # Error handling helper methods
    def _is_timeout_error(self, error_str: str) -> bool:
        return "timeout" in error_str or "read timed out" in error_str or "timed out" in error_str

    def _is_rate_limit_error(self, error_str: str) -> bool:
        return "429" in error_str or "quota" in error_str or "rate limit" in error_str

    def _is_token_limit_error(self, error_str: str) -> bool:
        return (
            "TOKEN_LIMIT_NO_CONTENT" in error_str or
            "token limit before generating" in error_str or
            ("max_tokens" in error_str and "prompt" in error_str.lower())
        )

    def _is_blocking_error(self, error_str: str) -> bool:
        return "safety" in error_str.lower() or "recitation" in error_str.lower()

    def _handle_timeout_retry(self, timeout: int, attempt: int) -> tuple:
        """Calculate new timeout and wait time for retry"""
        retry_timeout = min(timeout * 1.5, 300)
        wait_time = min(5 * (attempt + 1), 20)
        print(f"Request timed out, retrying with {retry_timeout}s timeout in {wait_time}s...")
        return int(retry_timeout), wait_time

    def _calculate_rate_limit_delay(self, error_message: str) -> float:
        """Calculate retry delay for rate limiting"""
        model_name = self.model.lower()

        # Default delays based on model type
        if "flash" in model_name:
            retry_delay = 40.0
        else:
            retry_delay = 50.0

        # Try to extract delay from error message
        delay_patterns = [
            r'retry\s+in\s+(\d+(?:\.\d+)?)\s*s\.?',
            r'retry\s+in\s+(\d+(?:\.\d+)?)',
            r'retry_delay\s*\{\s*seconds\s*:\s*(\d+)',
            r'(\d+(?:\.\d+)?)\s*seconds',
        ]

        for pattern in delay_patterns:
            delay_match = re.search(pattern, error_message, re.IGNORECASE)
            if delay_match:
                extracted_delay = float(delay_match.group(1))
                if "flash" in model_name:
                    retry_delay = max(extracted_delay + 5, 35)
                else:
                    retry_delay = max(extracted_delay + 10, 45)
                break

        return retry_delay

    def _handle_token_limit(self, prompt: str, max_tokens: int, attempt: int) -> tuple:
        """Handle token limit errors by reducing prompt or max_tokens"""
        # Try to truncate prompt if possible
        if "ACADEMIC CONTENT:\n" in prompt:
            parts = prompt.split("ACADEMIC CONTENT:\n", 1)
            if len(parts) == 2:
                base_prompt = parts[0] + "ACADEMIC CONTENT:\n"
                input_text_section = parts[1]

                if "\n\n(This is educational" in input_text_section:
                    text_parts = input_text_section.split("\n\n(This is educational", 1)
                    actual_text = text_parts[0]
                    rest = "\n\n(This is educational" + text_parts[1] if len(text_parts) > 1 else ""

                    truncated_length = int(len(actual_text) * 0.7)
                    truncated_text = actual_text[:truncated_length] + "...\n[Content truncated due to length]"

                    new_prompt = base_prompt + truncated_text + rest
                    print(f"Retry {attempt + 1}: Truncated input text due to token limit")
                    return new_prompt, max_tokens

        # If can't truncate, reduce max_tokens
        if max_tokens > 5000:
            new_max_tokens = int(max_tokens * 0.5)
            print(f"Retry {attempt + 1}: Reduced max_tokens to {new_max_tokens}")
            return prompt, new_max_tokens

        return prompt, max_tokens


class OpenAIStrategy(LLMStrategy):
    """
    Concrete strategy for OpenAI API.

    Implements the LLM generation using OpenAI's chat completions API.
    """

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def get_provider_name(self) -> str:
        return "openai"

    def generate(
        self,
        prompt: str,
        max_tokens: int,
        timeout: int = 60,
        max_retries: int = 3
    ) -> LLMResponse:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return LLMResponse(
                text=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens,
                model=self.model,
                provider="openai"
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class LocalStrategy(LLMStrategy):
    """
    Concrete strategy for local/fallback processing.

    Provides simple extractive summarization when no LLM provider is configured.
    """

    def get_provider_name(self) -> str:
        return "local"

    def generate(
        self,
        prompt: str,
        max_tokens: int,
        timeout: int = 60,
        max_retries: int = 3
    ) -> LLMResponse:
        """Simple extractive summary as fallback"""
        # Extract text from prompt (remove instruction parts)
        text = self._extract_text_from_prompt(prompt)
        summary = self._simple_summary(text)

        return LLMResponse(
            text=summary,
            tokens_used=0,
            model="simple",
            provider="local"
        )

    def _extract_text_from_prompt(self, prompt: str) -> str:
        """Extract actual text content from formatted prompt"""
        if "ACADEMIC CONTENT:\n" in prompt:
            parts = prompt.split("ACADEMIC CONTENT:\n")
            if len(parts) > 1:
                content = parts[1]
                if "\n\n(This is educational" in content:
                    return content.split("\n\n(This is educational")[0]
                return content
        return prompt

    def _simple_summary(self, text: str, max_sentences: int = 5) -> str:
        """Simple extractive summary"""
        try:
            import nltk
            sentences = nltk.sent_tokenize(text)
            return " ".join(sentences[:max_sentences])
        except:
            # Fallback if nltk not available
            sentences = text.split('. ')
            return '. '.join(sentences[:max_sentences])
