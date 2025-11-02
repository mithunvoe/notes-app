# API Usage Guide

## Getting Started

### 1. Upload a PDF

**Endpoint**: `POST /upload`

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@research-paper.pdf" \
  -F "user_prompt=Focus on methodology and results"
```

**Python Example**:
```python
import requests

url = "http://localhost:8000/upload"
files = {'file': open('research-paper.pdf', 'rb')}
data = {'user_prompt': 'Focus on methodology and results'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Response**:
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "abc123-task-id",
  "filename": "research-paper.pdf",
  "status": "uploaded",
  "message": "File uploaded successfully and queued for processing"
}
```

### 2. Check Processing Status

**Endpoint**: `GET /status/{file_id}`

**cURL Example**:
```bash
curl "http://localhost:8000/status/550e8400-e29b-41d4-a716-446655440000"
```

**Python Example**:
```python
import requests

file_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f"http://localhost:8000/status/{file_id}")
print(response.json())
```

**Response**:
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "research-paper.pdf",
  "status": "completed",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T10:05:00Z",
  "error": null
}
```

**Status Values**:
- `uploaded`: File saved, awaiting processing
- `processing`: Extracting and chunking text
- `indexed`: Text indexed in vector database
- `summarizing`: Generating chunk summaries
- `completed`: Notes ready
- `failed`: Processing failed (check error field)

### 3. Get Generated Notes

**Endpoint**: `GET /notes/{file_id}`

**cURL Example**:
```bash
curl "http://localhost:8000/notes/550e8400-e29b-41d4-a716-446655440000"
```

**Python Example**:
```python
import requests

file_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f"http://localhost:8000/notes/{file_id}")
note = response.json()

print(f"Note:\n{note['note_text']}")
```

**Response**:
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "note_text": "# Research Paper Summary\n\n## Methodology\n...\n\n## Results\n...",
  "metadata": {
    "total_chunks": 25,
    "synthesis_method": "hierarchical"
  },
  "created_at": "2025-11-01T10:05:00Z"
}
```

### 4. Ask Questions (RAG)

**Endpoint**: `POST /qa/{file_id}`

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/qa/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What methodology was used in this study?",
    "n_results": 5
  }'
```

**Python Example**:
```python
import requests

file_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:8000/qa/{file_id}"

payload = {
    "question": "What methodology was used in this study?",
    "n_results": 5
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Answer: {result['answer']}\n")
print(f"Sources: {len(result['sources'])} chunks used")
```

**Response**:
```json
{
  "answer": "The study used a mixed-methods approach combining quantitative surveys (n=500) and qualitative interviews (n=20)...",
  "sources": [
    {
      "chunk_index": 5,
      "relevance_score": 0.89,
      "preview": "The methodology section describes a mixed-methods approach..."
    },
    {
      "chunk_index": 6,
      "relevance_score": 0.85,
      "preview": "Data collection involved structured surveys distributed..."
    }
  ],
  "model_info": {
    "provider": "gemini",
    "model": "gemini-pro",
    "tokens_used": 450
  }
}
```

## Advanced Usage

### Polling for Completion

```python
import requests
import time

def wait_for_completion(file_id, timeout=600, interval=5):
    """Poll status endpoint until processing completes"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f"http://localhost:8000/status/{file_id}")
        data = response.json()
        
        status = data['status']
        print(f"Status: {status}")
        
        if status == 'completed':
            return True
        elif status == 'failed':
            print(f"Error: {data.get('error')}")
            return False
        
        time.time.sleep(interval)
    
    print("Timeout waiting for completion")
    return False

# Usage
file_id = upload_pdf('document.pdf')
if wait_for_completion(file_id):
    notes = get_notes(file_id)
```

### Batch Processing

```python
import requests
from pathlib import Path

def process_directory(directory_path):
    """Upload and process all PDFs in a directory"""
    results = []
    
    for pdf_file in Path(directory_path).glob('*.pdf'):
        print(f"Processing: {pdf_file.name}")
        
        with open(pdf_file, 'rb') as f:
            response = requests.post(
                "http://localhost:8000/upload",
                files={'file': f}
            )
        
        result = response.json()
        results.append({
            'filename': pdf_file.name,
            'file_id': result['file_id']
        })
    
    return results
```

### Custom Prompts

```python
# Detailed instructions for specific domains
user_prompts = {
    'research': 'Focus on methodology, results, and conclusions. Include statistical findings.',
    'legal': 'Extract key clauses, obligations, and important dates.',
    'technical': 'Summarize technical specifications, requirements, and implementation details.',
}

# Upload with custom prompt
response = requests.post(
    "http://localhost:8000/upload",
    files={'file': open('document.pdf', 'rb')},
    data={'user_prompt': user_prompts['research']}
)
```

### Interactive Q&A Session

```python
def qa_session(file_id):
    """Interactive question-answering session"""
    print("Ask questions about the document (type 'quit' to exit)")
    
    while True:
        question = input("\nQ: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        response = requests.post(
            f"http://localhost:8000/qa/{file_id}",
            json={'question': question, 'n_results': 5}
        )
        
        result = response.json()
        print(f"\nA: {result['answer']}")
        print(f"\n(Based on {len(result['sources'])} sources)")

# Usage
qa_session('550e8400-e29b-41d4-a716-446655440000')
```

## Client Libraries

### Python Client Class

```python
import requests
from typing import Optional, Dict, Any

class NotesAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def upload(self, file_path: str, user_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Upload a PDF file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'user_prompt': user_prompt} if user_prompt else {}
            response = requests.post(f"{self.base_url}/upload", files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def get_status(self, file_id: str) -> Dict[str, Any]:
        """Get file processing status"""
        response = requests.get(f"{self.base_url}/status/{file_id}")
        response.raise_for_status()
        return response.json()
    
    def get_notes(self, file_id: str) -> Dict[str, Any]:
        """Get generated notes"""
        response = requests.get(f"{self.base_url}/notes/{file_id}")
        response.raise_for_status()
        return response.json()
    
    def ask(self, file_id: str, question: str, n_results: int = 5) -> Dict[str, Any]:
        """Ask a question about the document"""
        response = requests.post(
            f"{self.base_url}/qa/{file_id}",
            json={'question': question, 'n_results': n_results}
        )
        response.raise_for_status()
        return response.json()
    
    def delete(self, file_id: str) -> Dict[str, Any]:
        """Delete a file"""
        response = requests.delete(f"{self.base_url}/files/{file_id}")
        response.raise_for_status()
        return response.json()

# Usage
client = NotesAPIClient()
result = client.upload('research.pdf', user_prompt='Focus on key findings')
file_id = result['file_id']

# Wait and get notes
import time
while client.get_status(file_id)['status'] != 'completed':
    time.sleep(5)

notes = client.get_notes(file_id)
print(notes['note_text'])
```

## Error Handling

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/upload",
        files={'file': open('document.pdf', 'rb')}
    )
    response.raise_for_status()
    result = response.json()
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        print("Bad request:", e.response.json()['detail'])
    elif e.response.status_code == 404:
        print("Not found:", e.response.json()['detail'])
    elif e.response.status_code == 500:
        print("Server error:", e.response.json()['detail'])
    else:
        print(f"HTTP error {e.response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("Cannot connect to API server")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Rate Limiting Considerations

When using external LLM APIs (Gemini/OpenAI), be aware of rate limits:

**Gemini Free Tier**:
- 60 requests per minute
- 1,500 requests per day

**Best Practices**:
```python
# For batch processing, add delays
import time

files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
for pdf in files:
    client.upload(pdf)
    time.sleep(2)  # Delay between uploads
```

## WebSocket Support (Future)

For real-time status updates, consider WebSocket integration:

```python
# Future implementation
import asyncio
import websockets

async def watch_status(file_id):
    uri = f"ws://localhost:8000/ws/status/{file_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            status = await websocket.recv()
            print(f"Status update: {status}")
            if status in ['completed', 'failed']:
                break
```
