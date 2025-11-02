from supabase import create_client, Client
from config import settings
from typing import Dict, Any, List, Optional
from datetime import datetime


class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # Files table operations
    def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new file record"""
        response = self.client.table('files').insert(file_data).execute()
        return response.data[0] if response.data else None
    
    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file by ID"""
        response = self.client.table('files').select('*').eq('id', file_id).execute()
        return response.data[0] if response.data else None
    
    def update_file_status(self, file_id: str, status: str, error: str = None) -> None:
        """Update file processing status"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow().isoformat()
        }
        if error:
            update_data['error'] = error
        self.client.table('files').update(update_data).eq('id', file_id).execute()
    
    def get_file_by_hash(self, sha256: str) -> Optional[Dict[str, Any]]:
        """Check if file with same hash exists"""
        response = self.client.table('files').select('*').eq('sha256', sha256).execute()
        return response.data[0] if response.data else None
    
    def delete_file(self, file_id: str) -> None:
        """Delete file record from database"""
        self.client.table('files').delete().eq('id', file_id).execute()
    
    def list_files(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List all files with pagination.
        
        Args:
            limit: Number of files to return (max 100)
            offset: Offset for pagination
        
        Returns:
            Dictionary with files list and total count
        """
        # Get total count
        count_response = self.client.table('files').select('*', count='exact').execute()
        total_count = count_response.count if hasattr(count_response, 'count') else 0
        
        # Get paginated files, ordered by most recent first
        response = self.client.table('files').select(
            'id, original_filename, file_size, status, created_at, updated_at, error'
        ).order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return {
            'files': response.data or [],
            'total': total_count,
            'limit': limit,
            'offset': offset
        }
    
    # Chunks table operations
    def create_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new chunk record"""
        response = self.client.table('chunks').insert(chunk_data).execute()
        return response.data[0] if response.data else None
    
    def get_chunks_by_file(self, file_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a file"""
        response = self.client.table('chunks').select('*').eq('file_id', file_id).order('chunk_index').execute()
        return response.data or []
    
    # Summaries table operations
    def create_summary(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new summary record"""
        response = self.client.table('summaries').insert(summary_data).execute()
        return response.data[0] if response.data else None
    
    def get_summaries_by_file(self, file_id: str) -> List[Dict[str, Any]]:
        """Get all summaries for a file"""
        response = self.client.table('summaries').select('*').eq('file_id', file_id).order('chunk_index').execute()
        return response.data or []
    
    def get_summary_by_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get summary for a specific chunk"""
        response = self.client.table('summaries').select('*').eq('chunk_id', chunk_id).execute()
        return response.data[0] if response.data else None
    
    # Notes table operations
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new note record"""
        response = self.client.table('notes').insert(note_data).execute()
        return response.data[0] if response.data else None
    
    def get_note_by_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get note for a file"""
        response = self.client.table('notes').select('*').eq('file_id', file_id).execute()
        return response.data[0] if response.data else None
    
    def update_note(self, file_id: str, note_text: str, metadata: Dict[str, Any] = None) -> None:
        """Update an existing note"""
        update_data = {
            'note_text': note_text,
            'updated_at': datetime.utcnow().isoformat()
        }
        if metadata:
            update_data['metadata'] = metadata
        self.client.table('notes').update(update_data).eq('file_id', file_id).execute()
    
    def delete_note(self, file_id: str) -> None:
        """Delete note for a file"""
        self.client.table('notes').delete().eq('file_id', file_id).execute()
    
    def delete_chunks(self, file_id: str) -> None:
        """Delete all chunks for a file (will cascade delete summaries)"""
        self.client.table('chunks').delete().eq('file_id', file_id).execute()
    
    def delete_summaries(self, file_id: str) -> None:
        """Delete all summaries for a file"""
        self.client.table('summaries').delete().eq('file_id', file_id).execute()
    
    def cleanup_file_data(self, file_id: str) -> None:
        """Clean up all processing data for a file (chunks, summaries, notes)"""
        # Delete notes first (since it has UNIQUE constraint)
        self.delete_note(file_id)
        # Delete chunks (will cascade delete summaries)
        self.delete_chunks(file_id)


# Global instance
db = SupabaseClient()
