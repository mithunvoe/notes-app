"""
State Machine Pattern Implementation for File Processing

This module implements the State Machine design pattern to manage the lifecycle
of file processing. It ensures valid state transitions and provides clear
visibility into the current processing state.

Benefits:
- Enforced valid state transitions (prevents invalid state changes)
- Centralized state management logic
- Audit trail of state changes
- Clear workflow visualization
- Prevents race conditions and invalid operations

States:
- uploaded: File has been uploaded but not yet processed
- processing: File is being processed (text extraction, chunking)
- indexed: File chunks are indexed in vector database
- summarizing: Summaries are being generated for chunks
- synthesizing: Final notes are being synthesized
- completed: All processing is done, notes are available
- failed: Processing failed at some point
"""

from enum import Enum
from typing import Optional, Callable, Dict, Any
from datetime import datetime
from transitions import Machine


class FileProcessingState(str, Enum):
    """
    Enumeration of all possible file processing states.
    Using Enum ensures type safety and prevents typos.
    """
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    SUMMARIZING = "summarizing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileStateMachine:
    """
    State Machine for managing file processing lifecycle.

    This class uses the 'transitions' library to implement a formal state machine
    with defined states and valid transitions. It prevents invalid state changes
    and provides callbacks for state changes.

    Example usage:
        fsm = FileStateMachine("file_123", db_update_callback)
        fsm.start_processing()  # uploaded -> processing
        fsm.finish_indexing()   # processing -> indexed
        fsm.start_summarizing() # indexed -> summarizing
        fsm.start_synthesizing() # summarizing -> synthesizing
        fsm.complete()          # synthesizing -> completed
    """

    # Define all valid states
    states = [state.value for state in FileProcessingState]

    # Define valid state transitions
    # Each transition has: trigger name, source state(s), destination state
    transitions = [
        # From uploaded
        {'trigger': 'start_processing', 'source': FileProcessingState.UPLOADED.value,
         'dest': FileProcessingState.PROCESSING.value},

        # From processing
        {'trigger': 'finish_indexing', 'source': FileProcessingState.PROCESSING.value,
         'dest': FileProcessingState.INDEXED.value},

        # From indexed
        {'trigger': 'start_summarizing', 'source': FileProcessingState.INDEXED.value,
         'dest': FileProcessingState.SUMMARIZING.value},

        # From summarizing
        {'trigger': 'start_synthesizing', 'source': FileProcessingState.SUMMARIZING.value,
         'dest': FileProcessingState.SYNTHESIZING.value},

        # From synthesizing
        {'trigger': 'complete', 'source': FileProcessingState.SYNTHESIZING.value,
         'dest': FileProcessingState.COMPLETED.value},

        # Failure can happen from any state except completed
        {'trigger': 'fail', 'source': [
            FileProcessingState.UPLOADED.value,
            FileProcessingState.PROCESSING.value,
            FileProcessingState.INDEXED.value,
            FileProcessingState.SUMMARIZING.value,
            FileProcessingState.SYNTHESIZING.value
         ], 'dest': FileProcessingState.FAILED.value},

        # Allow retry from failed state (go back to uploaded)
        {'trigger': 'retry', 'source': FileProcessingState.FAILED.value,
         'dest': FileProcessingState.UPLOADED.value},
    ]

    def __init__(
        self,
        file_id: str,
        update_callback: Optional[Callable[[str, str, Optional[str]], None]] = None,
        initial_state: str = FileProcessingState.UPLOADED.value
    ):
        """
        Initialize the state machine.

        Args:
            file_id: Unique identifier for the file
            update_callback: Function to call when state changes (e.g., DB update)
                           Signature: callback(file_id, new_state, error_message)
            initial_state: Starting state (default: uploaded)
        """
        self.file_id = file_id
        self.update_callback = update_callback
        self.error_message: Optional[str] = None
        self.state_history: list[Dict[str, Any]] = []

        # Initialize the state machine
        self.machine = Machine(
            model=self,
            states=FileStateMachine.states,
            transitions=FileStateMachine.transitions,
            initial=initial_state,
            after_state_change=self._on_state_change,
            auto_transitions=False  # Disable automatic transitions (require explicit triggers)
        )

        # Record initial state
        self._record_state_change(initial_state)

    def _on_state_change(self):
        """
        Callback triggered after any state change.

        This method:
        1. Records the state change in history
        2. Calls the update callback (e.g., to update database)
        3. Logs the transition
        """
        self._record_state_change(self.state)

        # Call update callback if provided
        if self.update_callback:
            self.update_callback(self.file_id, self.state, self.error_message)

        # Log the transition
        print(f"File {self.file_id}: State changed to {self.state}")

    def _record_state_change(self, new_state: str):
        """Record state change in history for audit trail"""
        self.state_history.append({
            'state': new_state,
            'timestamp': datetime.utcnow().isoformat(),
            'error': self.error_message
        })

    def fail(self, error_message: str):
        """
        Transition to failed state with error message.

        This override adds the error_message parameter to the auto-generated
        fail() trigger.

        Args:
            error_message: Description of the error that caused failure
        """
        self.error_message = error_message
        # The Machine will call the fail trigger which will transition to FAILED
        # and then call _on_state_change
        self.trigger('fail')

    def get_current_state(self) -> str:
        """Get the current state"""
        return self.state

    def get_state_history(self) -> list[Dict[str, Any]]:
        """Get the complete state transition history"""
        return self.state_history

    def can_transition_to(self, trigger_name: str) -> bool:
        """
        Check if a transition is currently valid.

        Args:
            trigger_name: Name of the transition trigger

        Returns:
            True if the transition is valid from current state
        """
        return self.machine.get_triggers(self.state).__contains__(trigger_name)

    def get_available_transitions(self) -> list[str]:
        """Get list of valid transitions from current state"""
        return self.machine.get_triggers(self.state)

    def is_terminal_state(self) -> bool:
        """Check if current state is terminal (completed or failed)"""
        return self.state in [FileProcessingState.COMPLETED.value, FileProcessingState.FAILED.value]

    def is_processing(self) -> bool:
        """Check if file is currently being processed"""
        return self.state in [
            FileProcessingState.PROCESSING.value,
            FileProcessingState.INDEXED.value,
            FileProcessingState.SUMMARIZING.value,
            FileProcessingState.SYNTHESIZING.value
        ]

    def can_query(self) -> bool:
        """Check if file is ready for Q&A queries"""
        # Can query once indexed (even if summarization is ongoing)
        return self.state in [
            FileProcessingState.INDEXED.value,
            FileProcessingState.SUMMARIZING.value,
            FileProcessingState.SYNTHESIZING.value,
            FileProcessingState.COMPLETED.value
        ]

    def can_get_notes(self) -> bool:
        """Check if notes are ready"""
        return self.state == FileProcessingState.COMPLETED.value

    def __repr__(self) -> str:
        return f"FileStateMachine(file_id={self.file_id}, state={self.state})"


def create_state_machine_from_db(file_id: str, current_status: str, update_callback) -> FileStateMachine:
    """
    Factory function to create a state machine from existing database state.

    This is useful when resuming processing or checking status of existing files.

    Args:
        file_id: File identifier
        current_status: Current status from database
        update_callback: Callback for state updates

    Returns:
        FileStateMachine initialized with the current state
    """
    # Validate that status is a valid state
    try:
        FileProcessingState(current_status)
    except ValueError:
        # Invalid status in DB, default to uploaded
        print(f"Warning: Invalid status '{current_status}' for file {file_id}, defaulting to 'uploaded'")
        current_status = FileProcessingState.UPLOADED.value

    return FileStateMachine(file_id, update_callback, initial_state=current_status)
