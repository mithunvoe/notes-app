"""
LLM Context - Strategy Pattern Context Class

This class acts as the Context in the Strategy pattern, providing a unified interface
for clients to use different LLM providers without knowing the implementation details.
"""

from typing import Dict, Any, Optional
from .llm_strategy import LLMStrategy, LLMResponse, GeminiStrategy, OpenAIStrategy, LocalStrategy
from config import settings


class LLMContext:
    """
    Context class for the Strategy pattern.

    This class maintains a reference to a Strategy object and delegates
    the work to the strategy. Clients interact with this context instead
    of directly with the strategies.
    """

    def __init__(self, strategy: Optional[LLMStrategy] = None):
        """
        Initialize with a strategy. If no strategy is provided,
        selects one based on configuration.
        """
        if strategy:
            self._strategy = strategy
        else:
            self._strategy = self._select_strategy_from_config()

    def _select_strategy_from_config(self) -> LLMStrategy:
        """
        Factory method to select strategy based on configuration.
        Demonstrates how the Context can automatically choose the right strategy.
        """
        provider = settings.llm_provider

        if provider == "gemini" and settings.gemini_api_key:
            return GeminiStrategy()
        elif provider == "openai" and settings.openai_api_key:
            return OpenAIStrategy()
        else:
            return LocalStrategy()

    def set_strategy(self, strategy: LLMStrategy):
        """
        Allow runtime strategy switching.
        This demonstrates the flexibility of the Strategy pattern.
        """
        self._strategy = strategy

    def get_current_provider(self) -> str:
        """Get the name of the current provider"""
        return self._strategy.get_provider_name()

    def _get_style_instructions(self, note_style: str) -> Dict[str, Any]:
        """Get style-specific instructions for note generation"""
        styles = {
            'short': {
                'instruction': """Create SHORT, easy-to-read notes:
- Use bullet points only
- Include ONLY the most important facts
- Keep each point to one simple sentence
- Focus on key takeaways
- Maximum 5-7 bullet points per section
- Use simple, everyday words
- Skip minor details""",
                'max_tokens': settings.gemini_max_output_tokens
            },
            'moderate': {
                'instruction': """Create BALANCED, clear notes:
- Mix bullet points and short paragraphs
- Include main ideas and important details
- Explain concepts in simple terms
- Add brief examples when helpful
- Organize by topics/sections
- Use easy-to-understand language
- Keep explanations brief but clear""",
                'max_tokens': settings.gemini_max_output_tokens
            },
            'descriptive': {
                'instruction': """Create DETAILED, comprehensive notes:
- Use full paragraphs with complete explanations
- Include all important information and context
- Explain concepts thoroughly in simple language
- Add examples and details to clarify points
- Organize into clear sections with headings
- Break down complex ideas into easy steps
- Include background information when needed
- Make sure anyone can understand the content""",
                'max_tokens': settings.gemini_max_output_tokens
            }
        }
        return styles.get(note_style, styles['moderate'])

    def generate_summary(
        self,
        text: str,
        note_style: str = "moderate",
        user_prompt: Optional[str] = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """
        Generate a summary of the given text.

        This method builds the prompt and delegates to the current strategy.
        """
        style_config = self._get_style_instructions(note_style)
        if max_tokens is None:
            max_tokens = style_config['max_tokens']

        # Build prompt with academic context
        academic_context = """IMPORTANT ACADEMIC CONTEXT: This is EDUCATIONAL CONTENT from university lecture slides or textbooks.

CONTENT TYPE: Academic content including formulas, equations, technical terminology, scientific concepts, historical facts, literature analysis, or any educational material and everything academic.

EDUCATIONAL PURPOSE: This is for academic learning. All technical terms, formulas, equations, concepts, and subject-specific terminology are standard educational content and everything academic.

SAFETY INSTRUCTION: Process ALL academic notation, formulas, equations, technical terms, and educational content normally. This is safe educational material. Do not block any academic or educational content."""

        base_prompt = f"""{academic_context}

You are a helpful note-taking assistant for academic content. Your job is to create notes that are very easy to understand.

{style_config['instruction']}"""

        if user_prompt:
            base_prompt += f"\n\nAdditional instructions: {user_prompt}"

        wrapped_text = f"ACADEMIC CONTENT:\n{text}\n\n(This is educational material from academic sources)"
        prompt = f"{base_prompt}\n\n{wrapped_text}\n\nEDUCATIONAL NOTES:"

        # Delegate to strategy
        response = self._strategy.generate(prompt, max_tokens)
        return response.to_dict()

    def synthesize_notes(
        self,
        summaries: list[str],
        note_style: str = "moderate",
        user_prompt: Optional[str] = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """
        Synthesize multiple summaries into a cohesive note.

        This method builds the synthesis prompt and delegates to the current strategy.
        """
        style_config = self._get_style_instructions(note_style)
        if max_tokens is None:
            max_tokens = settings.gemini_max_output_tokens

        # Build prompt based on style
        academic_context = "IMPORTANT: This is educational academic content. Process all formulas, equations, technical terms, and subject-specific terminology completely.\n\n"

        if note_style == 'short':
            base_prompt = f"""{academic_context}You are a helpful note-taking assistant for academic content. Combine these section notes into ONE SHORT, easy-to-read final note.

This is educational/academic content. Process all formulas, equations, technical terminology, and subject-specific content normally.

Instructions:
- Create a simple bullet-point list
- Include only the MOST IMPORTANT points from all sections
- Use very simple, clear language
- Maximum 10-15 bullet points total
- Remove any repeated information
- Keep each point to one simple sentence"""

        elif note_style == 'descriptive':
            base_prompt = f"""{academic_context}You are a helpful note-taking assistant for academic content. Combine these section notes into ONE DETAILED, comprehensive final note.

This is educational/academic content. Process all formulas, equations, technical terminology, and subject-specific content normally.

CRITICAL INSTRUCTIONS FOR DESCRIPTIVE NOTES:
- Write in full, detailed paragraphs with complete explanations
- Include ALL important information from ALL sections - do not skip any significant details
- For each concept, provide thorough explanations with context and background
- Include all formulas, equations, definitions, theorems, examples, concepts, and key information from every section
- Explain the reasoning behind concepts and theories
- Show how different concepts relate to each other
- Organize into clear, well-structured sections with descriptive headings
- Use subheadings to break down complex topics
- Provide step-by-step explanations where appropriate
- Include examples and applications when mentioned in the source material
- Write as if you're creating comprehensive study notes - be thorough and complete
- Make sure anyone can understand the content without referring to the original material
- Remove only truly redundant information, but keep all important details even if somewhat related"""

        else:  # moderate
            base_prompt = f"""{academic_context}You are a helpful note-taking assistant for academic content. Combine these section notes into ONE BALANCED, clear final note.

This is educational/academic content. Process all formulas, equations, technical terminology, and subject-specific content normally.

Instructions:
- Mix bullet points and short paragraphs
- Include main ideas and key details from all sections
- Use clear, simple language
- Organize by main topics
- Remove repeated information
- Keep explanations brief but complete
- Make it easy to read and understand"""

        if user_prompt:
            base_prompt += f"\n\nExtra instructions from user: {user_prompt}"

        # Format summaries
        combined_summaries = "\n\n---\n\n".join(f"Section {i+1}:\n{s}" for i, s in enumerate(summaries))

        if note_style == 'descriptive':
            synthesis_instruction = f"""\n\nIMPORTANT: You are combining {len(summaries)} section summaries. Your final note MUST include comprehensive information from ALL {len(summaries)} sections above. Be thorough and detailed - this is a descriptive note that should cover everything important from all the sections.\n\nSection notes to combine:\n\n{combined_summaries}\n\nFinal Note (DESCRIPTIVE - include all details from all sections):"""
        else:
            synthesis_instruction = f"\n\nSection notes to combine:\n\n{combined_summaries}\n\nFinal Note:"

        prompt = f"{base_prompt}{synthesis_instruction}"

        # Calculate timeout for synthesis (can take longer)
        synthesis_timeout = max(120, int(max_tokens / 50))
        synthesis_timeout = min(synthesis_timeout, 300)

        # Delegate to strategy
        response = self._strategy.generate(prompt, max_tokens, timeout=synthesis_timeout)
        return response.to_dict()

    def answer_question(
        self,
        question: str,
        context_chunks: list[str],
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Answer a question based on provided context.

        This method builds the Q&A prompt and delegates to the current strategy.
        """
        prompt = """You are a helpful assistant. Answer the question using the information provided below.
Use simple, easy-to-understand language. If the information isn't in the sources, say so clearly.
When possible, mention which source number your answer comes from.

Sources:
"""
        for i, chunk in enumerate(context_chunks, 1):
            prompt += f"\n[Source {i}]\n{chunk}\n"

        prompt += f"\n\nQuestion: {question}\n\nAnswer:"

        # Delegate to strategy
        response = self._strategy.generate(prompt, max_tokens)
        return response.to_dict()
