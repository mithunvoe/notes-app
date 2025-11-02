import pytest
import requests
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "test_sample.pdf"  # You'll need to provide a test PDF


class TestNotesAPI:
    """Integration tests for Notes API"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'chroma' in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert 'version' in data
        assert 'endpoints' in data
    
    @pytest.mark.skipif(not Path(TEST_PDF_PATH).exists(), 
                        reason="Test PDF not found")
    def test_upload_pdf(self):
        """Test PDF upload"""
        with open(TEST_PDF_PATH, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/upload",
                files={'file': f},
                data={'user_prompt': 'Test prompt'}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert 'file_id' in data
        assert 'task_id' in data
        assert data['status'] == 'uploaded'
        
        return data['file_id']
    
    def test_upload_invalid_file(self):
        """Test upload with non-PDF file"""
        # Create a temporary text file
        with open('test.txt', 'w') as f:
            f.write('This is not a PDF')
        
        try:
            with open('test.txt', 'rb') as f:
                response = requests.post(
                    f"{BASE_URL}/upload",
                    files={'file': ('test.txt', f)}
                )
            
            assert response.status_code == 400
            assert 'PDF' in response.json()['detail']
        finally:
            Path('test.txt').unlink()
    
    @pytest.mark.skipif(not Path(TEST_PDF_PATH).exists(),
                        reason="Test PDF not found")
    def test_full_workflow(self):
        """Test complete workflow: upload -> process -> get notes -> Q&A"""
        
        # 1. Upload
        print("\n1. Uploading PDF...")
        with open(TEST_PDF_PATH, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/upload",
                files={'file': f}
            )
        assert response.status_code == 200
        file_id = response.json()['file_id']
        print(f"   File ID: {file_id}")
        
        # 2. Wait for processing
        print("\n2. Waiting for processing...")
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(f"{BASE_URL}/status/{file_id}")
            assert response.status_code == 200
            
            status_data = response.json()
            status = status_data['status']
            print(f"   Status: {status}")
            
            if status == 'completed':
                break
            elif status == 'failed':
                pytest.fail(f"Processing failed: {status_data.get('error')}")
            
            time.sleep(5)
        else:
            pytest.fail("Timeout waiting for processing")
        
        # 3. Get notes
        print("\n3. Retrieving notes...")
        response = requests.get(f"{BASE_URL}/notes/{file_id}")
        assert response.status_code == 200
        notes_data = response.json()
        assert 'note_text' in notes_data
        assert len(notes_data['note_text']) > 0
        print(f"   Note length: {len(notes_data['note_text'])} chars")
        
        # 4. Ask a question
        print("\n4. Testing Q&A...")
        response = requests.post(
            f"{BASE_URL}/qa/{file_id}",
            json={
                'question': 'What is this document about?',
                'n_results': 3
            }
        )
        assert response.status_code == 200
        qa_data = response.json()
        assert 'answer' in qa_data
        assert 'sources' in qa_data
        assert len(qa_data['sources']) > 0
        print(f"   Answer: {qa_data['answer'][:100]}...")
        print(f"   Sources: {len(qa_data['sources'])}")
        
        # 5. Delete file
        print("\n5. Cleaning up...")
        response = requests.delete(f"{BASE_URL}/files/{file_id}")
        assert response.status_code == 200
        print("   ✓ Test completed successfully")


def test_api_documentation():
    """Test that API documentation is accessible"""
    # Test OpenAPI schema
    response = requests.get(f"{BASE_URL}/openapi.json")
    assert response.status_code == 200
    
    # Test Swagger UI
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200
    
    # Test ReDoc
    response = requests.get(f"{BASE_URL}/redoc")
    assert response.status_code == 200


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '-s'])
