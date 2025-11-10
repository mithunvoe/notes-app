from typing import Optional

# Local imports kept here to avoid circulars elsewhere
from database import db


class FileState:
    """
    Base class for file processing states.
    Each concrete state sets the status in the database when entered.
    """

    name: str = ""

    def enter(self, file_id: str, error: Optional[str] = None) -> None:
        if self.name == "failed":
            db.update_file_status(file_id, self.name, error=error)
        else:
            db.update_file_status(file_id, self.name)


class UploadedState(FileState):
    name = "uploaded"


class ProcessingState(FileState):
    name = "processing"


class IndexedState(FileState):
    name = "indexed"


class SummarizingState(FileState):
    name = "summarizing"


class CompletedState(FileState):
    name = "completed"


class FailedState(FileState):
    name = "failed"


class FileProcessingContext:
    """
    Context that owns the current state of file processing and applies transitions.
    """

    def __init__(self, file_id: str):
        self.file_id = file_id
        self._state: FileState = UploadedState()

    def set_state(self, state: FileState, error: Optional[str] = None) -> None:
        self._state = state
        # Entering a state updates the DB
        self._state.enter(self.file_id, error=error)

    # Convenience transition helpers
    def to_uploaded(self) -> None:
        self.set_state(UploadedState())

    def to_processing(self) -> None:
        self.set_state(ProcessingState())

    def to_indexed(self) -> None:
        self.set_state(IndexedState())

    def to_summarizing(self) -> None:
        self.set_state(SummarizingState())

    def to_completed(self) -> None:
        self.set_state(CompletedState())

    def to_failed(self, error: str) -> None:
        self.set_state(FailedState(), error=error)


