from celery import Task
from celery_app import celery
from typing import List, Dict, Any
import os
import time
import re
from datetime import datetime

from database import db
from chroma_client import chroma_service
# Use new Strategy Pattern for LLM
from patterns.strategy import LLMContext
# Use new State Machine Pattern for file processing
from patterns.state_machine import FileStateMachine, create_state_machine_from_db
from config import settings
from utils import (
    extract_text_from_pdf,
    TextChunker,
    embedding_service,
    get_pdf_metadata,
    save_note_as_markdown,
    get_note_filename
)

# Initialize LLM context with strategy pattern
llm_context = LLMContext()  # Auto-selects strategy based on config


def db_update_callback(file_id: str, new_state: str, error_message: str = None):
    """
    Callback function for state machine to update database.
    This decouples the state machine from database implementation.
    """
    db.update_file_status(file_id, new_state, error=error_message)


def convert_pseudo_code_to_math(note_text: str) -> str:
    """
    Convert pseudo-code blocks containing mathematical notation to LaTeX equations.
    
    Detects code blocks that contain mathematical notation (subscripts, fractions, etc.)
    and converts them to proper LaTeX display math blocks.
    
    Args:
        note_text: The markdown note text
        
    Returns:
        Processed markdown text with pseudo-code converted to math equations
    """
    # Pattern to match code blocks (```...``` or with language identifier)
    code_block_pattern = r'```(?:[a-zA-Z]*)?\n?(.*?)```'
    
    def process_code_block(match):
        code_content = match.group(1).strip()
        
        # Check if the code block contains mathematical notation
        # Look for patterns like: _{}, fractions (/), subscripts, etc.
        has_math_notation = (
            re.search(r'_\s*\{[^}]+\}', code_content) or  # Subscripts like b_{L[n]}
            re.search(r'[a-zA-Z]+\s*/\s*[a-zA-Z]+', code_content) or  # Fractions like b/a
            re.search(r'=\s*[a-zA-Z]+\s*/\s*[a-zA-Z]+', code_content)  # Assignments with fractions
        )
        
        # Check if it looks like pseudo-code with math (has comments and math notation)
        has_comments = '//' in code_content or ('#' in code_content and not code_content.strip().startswith('#'))
        has_loops = bool(re.search(r'\b(Do|For|While|End|downto|to)\b', code_content, re.IGNORECASE))
        
        # If it contains math notation and looks like pseudo-code, convert to math equations
        if has_math_notation and (has_comments or has_loops):
            # Extract mathematical expressions and convert them
            lines = code_content.split('\n')
            math_lines = []
            
            for line in lines:
                original_line = line
                # Remove comments
                if '//' in line:
                    line = line[:line.index('//')].strip()
                elif '#' in line and not line.strip().startswith('#'):
                    # Check if # is part of a heading (not a comment)
                    if not re.match(r'^\s*#+\s+', line):
                        line = line[:line.index('#')].strip()
                
                # Skip loop control structures (they're not math equations)
                if re.search(r'\b(Do|For|While|End|downto|to)\b', line, re.IGNORECASE):
                    # Try to extract any math from these lines
                    # For example, "Do i = n-1 downto 1" could become "i = n-1, \ldots, 1"
                    if '=' in line:
                        parts = line.split('=')
                        if len(parts) == 2:
                            var_part = parts[0].strip()
                            expr_part = parts[1].strip()
                            # Extract math expressions
                            if has_math_notation or re.search(r'[0-9]', expr_part):
                                # Convert to math notation
                                math_lines.append(f"{var_part} = {expr_part}")
                    continue
                
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('#'):
                    # Convert mathematical expressions to proper LaTeX
                    # First, fix patterns like b_{L[n]} to ensure proper LaTeX formatting
                    # Replace patterns like xn (where n is a number) with x_n
                    line = re.sub(r'\b([a-zA-Z]+)([0-9]+)\b', r'\1_{\2}', line)
                    # Replace patterns like xj, xi (where j/i are letters) with x_j, x_i  
                    line = re.sub(r'\b([a-zA-Z]+)([ij])\b(?![\w])', r'\1_{\2}', line)
                    # Ensure subscripts are properly formatted
                    # Patterns like a_{L[i],j} are already correct, but ensure spacing
                    line = re.sub(r'_\s*\{', r'_{', line)
                    
                    # Convert division operations to fractions where appropriate
                    # But be careful not to break variable names
                    line = re.sub(r'([a-zA-Z0-9_]+)\s*/\s*([a-zA-Z0-9_]+)', r'\\frac{\1}{\2}', line)
                    
                    math_lines.append(line)
            
            if math_lines:
                # Combine into a math display block with proper LaTeX formatting
                math_content = ' \\\\\n'.join(math_lines)  # Use \\ for line breaks in LaTeX
                # Wrap in LaTeX display math block
                return f'\n$$\n\\begin{{aligned}}\n{math_content}\n\\end{{aligned}}\n$$\n'
        
        # Otherwise, keep as code block
        return match.group(0)
    
    # Process all code blocks
    processed_text = re.sub(code_block_pattern, process_code_block, note_text, flags=re.DOTALL | re.MULTILINE)
    
    return processed_text


class CallbackTask(Task):
    """Base task with error handling"""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure - using State Machine pattern"""
        file_id = args[0] if args else None
        if file_id:
            try:
                # Create state machine with current state from DB
                file_info = db.get_file(file_id)
                current_status = file_info['status'] if file_info else 'uploaded'
                fsm = create_state_machine_from_db(file_id, current_status, db_update_callback)
                fsm.fail(str(exc))
            except Exception:
                # Fallback to direct update if state machine has issues
                db.update_file_status(file_id, 'failed', error=str(exc))


@celery.task(bind=True, base=CallbackTask, acks_late=True, max_retries=3)
def process_file_task(self, file_id: str, file_path: str, note_style: str = "moderate", user_prompt: str = None):
    """
    Main task to process uploaded PDF file.
    
    Steps:
    1. Extract text from PDF
    2. Chunk text with sentence awareness
    3. Compute embeddings
    4. Store in Chroma and database
    5. Enqueue summarization tasks
    
    Args:
        file_id: Unique file identifier
        file_path: Path to PDF file
        note_style: Style of notes ('short', 'moderate', or 'descriptive')
        user_prompt: Optional custom instructions
    """
    try:
        # Use State Machine pattern for file processing states
        fsm = FileStateMachine(file_id, db_update_callback)
        fsm.start_processing()
        
        # Step 1: Extract text
        self.update_state(state='PROGRESS', meta={'step': 'extracting_text'})
        text = extract_text_from_pdf(file_path)
        pdf_metadata = get_pdf_metadata(file_path)
        
        if not text or len(text.strip()) < 100:
            raise ValueError("Extracted text is too short or empty. PDF may be image-based.")
        
        # Step 2: Chunk text
        self.update_state(state='PROGRESS', meta={'step': 'chunking_text'})
        chunker = TextChunker()
        chunks = chunker.chunk_text(text)
        
        if not chunks:
            raise ValueError("No chunks created from text")
        
        # Step 3: Compute embeddings in batches
        self.update_state(state='PROGRESS', meta={'step': 'computing_embeddings'})
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts, show_progress=False)
        
        # Step 4: Prepare data for Chroma and database
        self.update_state(state='PROGRESS', meta={'step': 'storing_chunks'})
        chunk_ids = []
        documents = []
        metadatas = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{file_id}__{i}"
            chunk_ids.append(chunk_id)
            documents.append(chunk['text'])
            
            metadata = {
                'file_id': file_id,
                'chunk_index': i,
                'token_count': chunk['token_count']
            }
            metadatas.append(metadata)
            
            # Store chunk in database
            db.create_chunk({
                'file_id': file_id,
                'chunk_id': chunk_id,
                'chunk_index': i,
                'chunk_text': chunk['text'],
                'token_count': chunk['token_count']
            })
        
        # Step 5: Store in Chroma
        chroma_service.add_chunks(
            documents=documents,
            metadatas=metadatas,
            ids=chunk_ids,
            embeddings=embeddings
        )
        
        # Use State Machine: transition to indexed
        fsm.finish_indexing()
        
        # Step 6: Enqueue summarization task with note style
        self.update_state(state='PROGRESS', meta={'step': 'enqueuing_summarization'})
        summarize_chunks_task.delay(file_id, chunk_ids, note_style, user_prompt)
        
        return {
            'status': 'indexed',
            'chunks_created': len(chunk_ids),
            'total_tokens': sum(c['token_count'] for c in chunks),
            'pdf_metadata': pdf_metadata
        }

    except Exception as e:
        # Use State Machine: transition to failed
        try:
            fsm.fail(str(e))
        except Exception:
            # Fallback to direct update if state machine fails
            db.update_file_status(file_id, 'failed', error=str(e))
        raise


@celery.task(bind=True, base=CallbackTask, acks_late=True, max_retries=2)
def summarize_chunks_task(self, file_id: str, chunk_ids: List[str], note_style: str = "moderate", user_prompt: str = None):
    """
    Summarize all chunks for a file in the specified style.
    
    Args:
        file_id: File ID
        chunk_ids: List of chunk IDs to summarize
        note_style: Style of notes ('short', 'moderate', or 'descriptive')
        user_prompt: Optional custom instructions
    """
    try:
        # Use State Machine: transition to summarizing
        file_info = db.get_file(file_id)
        current_status = file_info['status'] if file_info else 'indexed'
        fsm = create_state_machine_from_db(file_id, current_status, db_update_callback)
        fsm.start_summarizing()
        
        # Get chunks from database
        chunks = db.get_chunks_by_file(file_id)
        
        if not chunks:
            raise ValueError("No chunks found for file")
        
        summaries = []
        total_tokens = 0
        successful_summaries = 0
        failed_summaries = 0
        
        for i, chunk in enumerate(chunks):
            self.update_state(
                state='PROGRESS',
                meta={
                    'step': 'summarizing_chunks',
                    'current': i + 1,
                    'total': len(chunks)
                }
            )
            
            # Generate summary for chunk with specified style using Strategy Pattern
            try:
                result = llm_context.generate_summary(
                    chunk['chunk_text'],
                    note_style=note_style,
                    user_prompt=user_prompt
                )
                
                # Validate that result contains required fields
                if not result or not result.get('text'):
                    raise ValueError(f"LLM service returned empty result for chunk {chunk['chunk_id']}")
                
                # Store summary in database
                summary_data = {
                    'file_id': file_id,
                    'chunk_id': chunk['chunk_id'],
                    'chunk_index': chunk['chunk_index'],
                    'summary_text': result['text'],
                    'llm_provider': result.get('provider', 'unknown'),
                    'llm_model': result.get('model', 'unknown'),
                    'tokens_used': result.get('tokens_used', 0)
                }
                db.create_summary(summary_data)
                
                summaries.append(result['text'])
                total_tokens += result.get('tokens_used', 0)
                successful_summaries += 1
                
                # Rate limiting: Gemini free tier allows 10 requests/minute for Flash, 2 for Pro
                # Add delay between chunk summaries to respect rate limits
                # NOTE: This manual rate limiting will be replaced by Decorator pattern in future
                if llm_context.get_current_provider() == "gemini" and i < len(chunks) - 1:  # Don't delay after last chunk
                    # Check if using Flash (10 RPM) or Pro (2 RPM) model
                    model_name = settings.gemini_model.lower()
                    if "flash" in model_name:
                        # Flash: 10 requests/minute = 6 seconds per request, use 7 seconds for safety
                        delay = 7
                    else:
                        # Pro: 2 requests/minute = 30 seconds per request, use 45 seconds for extra safety
                        # Need extra buffer due to retry logic potentially making multiple requests
                        delay = 45
                    print(f"Rate limiting: waiting {delay} seconds before processing next chunk...")
                    time.sleep(delay)
                
            except Exception as e:
                # If individual chunk fails, log but continue
                failed_summaries += 1
                error_msg = f"Error summarizing chunk {chunk['chunk_id']}: {str(e)}"
                print(error_msg)
                
                # Fallback for safety blocks: extract key sentences from the chunk
                if "SAFETY" in str(e) or "blocked" in str(e).lower():
                    try:
                        # Simple extractive summary as fallback
                        sentences = chunk['chunk_text'].split('.')
                        # Get first few meaningful sentences (skip empty ones)
                        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
                        if key_sentences:
                            fallback_summary = ". ".join(key_sentences) + "."
                            print(f"Using fallback summary for chunk {chunk['chunk_id']} due to safety block")
                            
                            # Store fallback summary
                            summary_data = {
                                'file_id': file_id,
                                'chunk_id': chunk['chunk_id'],
                                'chunk_index': chunk['chunk_index'],
                                'summary_text': f"[Fallback due to safety filter] {fallback_summary}",
                                'llm_provider': 'fallback',
                                'llm_model': 'extractive',
                                'tokens_used': 0
                            }
                            db.create_summary(summary_data)
                            summaries.append(fallback_summary)
                            successful_summaries += 1
                            continue  # Successfully created fallback, skip error handling
                    except Exception as fallback_error:
                        print(f"Fallback extraction also failed: {fallback_error}")
                
                # Don't add placeholder to summaries list - we need actual DB entries
                
                # If it's a rate limit error, wait longer before processing next chunk
                error_str = str(e).lower()
                if llm_context.get_current_provider() == "gemini" and ("429" in error_str or "quota" in error_str or "rate limit" in error_str):
                    if i < len(chunks) - 1:  # Don't delay after last chunk
                        # Try to extract retry delay from error message
                        import re
                        model_name = settings.gemini_model.lower()
                        if "flash" in model_name:
                            delay = 60  # Flash: wait 60 seconds after rate limit error
                        else:
                            delay = 90  # Pro: wait 90 seconds (1.5 minutes) after rate limit error for 2 req/min limit
                        error_msg = str(e)
                        # Match patterns like "retry in 33.19s." or "retry in 33 seconds"
                        delay_patterns = [
                            r'retry\s+in\s+(\d+(?:\.\d+)?)\s*s\.?',  # "retry in 33.19s" or "retry in 33.19s."
                            r'retry\s+in\s+(\d+(?:\.\d+)?)',  # "retry in 33.19"
                            r'(\d+(?:\.\d+)?)\s*seconds',  # "33 seconds"
                        ]
                        for pattern in delay_patterns:
                            delay_match = re.search(pattern, error_msg, re.IGNORECASE)
                            if delay_match:
                                extracted_delay = float(delay_match.group(1))
                                # Wait the extracted delay + 10 seconds buffer
                                delay = max(extracted_delay + 10, 40)  # At least 40 seconds
                                break
                        
                        print(f"Rate limit error encountered, waiting {delay:.1f} seconds before next chunk...")
                        time.sleep(delay)
        
        # Only enqueue synthesis if we have at least one successful summary
        if successful_summaries == 0:
            raise ValueError(
                f"Failed to create any summaries. "
                f"All {failed_summaries} chunks failed to summarize. "
                f"Check LLM service configuration and API keys."
            )
        
        # Enqueue synthesis task with note style
        self.update_state(state='PROGRESS', meta={'step': 'enqueuing_synthesis'})
        synthesize_notes_task.delay(file_id, note_style, user_prompt)
        
        return {
            'status': 'summarized',
            'summaries_created': successful_summaries,
            'failed_summaries': failed_summaries,
            'total_tokens': total_tokens
        }
        
    except Exception as e:
        # Use State Machine: transition to failed
        try:
            fsm.fail(str(e))
        except Exception:
            # Fallback to direct update if state machine fails
            db.update_file_status(file_id, 'failed', error=str(e))
        raise


@celery.task(bind=True, base=CallbackTask, acks_late=True, max_retries=2)
def synthesize_notes_task(self, file_id: str, note_style: str = "moderate", user_prompt: str = None):
    """
    Synthesize final notes from chunk summaries in the specified style.
    
    Args:
        file_id: File ID
        note_style: Style of notes ('short', 'moderate', or 'descriptive')
        user_prompt: Optional custom instructions
    """
    try:
        # Get all summaries for the file
        summaries = db.get_summaries_by_file(file_id)
        
        if not summaries:
            # Check if chunks exist to provide better error context
            chunks = db.get_chunks_by_file(file_id)
            chunks_count = len(chunks) if chunks else 0
            raise ValueError(
                f"No summaries found for synthesis. "
                f"File has {chunks_count} chunks but no summaries were created. "
                f"This may indicate that summarization failed for all chunks."
            )
        
        # Extract summary texts
        summary_texts = [s['summary_text'] for s in summaries]

        # Use State Machine: transition to synthesizing
        file_info = db.get_file(file_id)
        current_status = file_info['status'] if file_info else 'summarizing'
        fsm = create_state_machine_from_db(file_id, current_status, db_update_callback)
        fsm.start_synthesizing()

        # For hierarchical synthesis with many summaries, do it in stages using Strategy Pattern
        if len(summary_texts) > 20:
            # First level: synthesize in groups of 10
            intermediate_summaries = []
            for i in range(0, len(summary_texts), 10):
                group = summary_texts[i:i+10]
                result = llm_context.synthesize_notes(group, note_style, user_prompt)
                intermediate_summaries.append(result['text'])

            # Final synthesis with note style
            final_result = llm_context.synthesize_notes(intermediate_summaries, note_style, user_prompt)
        else:
            # Direct synthesis for smaller documents with note style
            final_result = llm_context.synthesize_notes(summary_texts, note_style, user_prompt)
        
        # Post-process: Convert pseudo-code blocks with math notation to LaTeX equations
        processed_note_text = convert_pseudo_code_to_math(final_result['text'])
        
        # Store final note
        note_data = {
            'file_id': file_id,
            'note_text': processed_note_text,
            'metadata': {
                'total_chunks': len(summaries),
                'synthesis_method': 'hierarchical' if len(summary_texts) > 20 else 'direct',
                'note_style': note_style
            },
            'llm_provider': final_result['provider'],
            'llm_model': final_result['model'],
            'tokens_used': final_result.get('tokens_used', 0)
        }
        db.create_note(note_data)
        
        # Save note as markdown file locally if enabled
        if settings.save_notes_locally:
            try:
                # Get file info to retrieve original filename
                file_info = db.get_file(file_id)
                original_filename = file_info.get('original_filename', '') if file_info else ''
                
                # Generate markdown filename
                md_filename = get_note_filename(original_filename, file_id)
                md_file_path = os.path.join(settings.notes_dir, md_filename)
                
                # Ensure notes directory exists
                os.makedirs(settings.notes_dir, exist_ok=True)
                
                # Prepare metadata for frontmatter
                frontmatter_metadata = {
                    'file_id': file_id,
                    'original_filename': original_filename,
                    'note_style': note_style,
                    'llm_provider': final_result.get('provider'),
                    'llm_model': final_result.get('model'),
                    'tokens_used': final_result.get('tokens_used', 0),
                }
                # Merge additional metadata
                if note_data.get('metadata'):
                    frontmatter_metadata.update(note_data['metadata'])
                
                # Save as markdown file (use processed note text with converted math)
                save_note_as_markdown(
                    note_text=processed_note_text,
                    output_path=md_file_path,
                    metadata=frontmatter_metadata
                )
                print(f"Note saved locally as markdown: {md_file_path}")
            except Exception as e:
                # Log error but don't fail the task
                print(f"Warning: Failed to save note locally as markdown: {str(e)}")
        
        # Use State Machine: transition to completed
        try:
            fsm.complete()
        except Exception:
            # Fallback to direct update if state machine fails
            db.update_file_status(file_id, 'completed')

        return {
            'status': 'completed',
            'note_length': len(processed_note_text),
            'tokens_used': final_result.get('tokens_used', 0)
        }

    except Exception as e:
        # Use State Machine: transition to failed
        try:
            fsm.fail(str(e))
        except Exception:
            # Fallback to direct update if state machine fails
            db.update_file_status(file_id, 'failed', error=str(e))
        raise


@celery.task(bind=True, acks_late=True)
def cleanup_old_files_task(self, days_old: int = 30):
    """
    Cleanup task to remove old processed files.
    
    Args:
        days_old: Remove files older than this many days
    """
    # This would be run periodically via Celery Beat
    # Implementation depends on your cleanup policy
    pass
