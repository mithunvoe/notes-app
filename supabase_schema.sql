-- Files table: stores uploaded PDF metadata
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    file_size BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'uploaded',  -- uploaded, processing, indexed, summarizing, completed, failed
    error TEXT,
    user_prompt TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX idx_files_sha256 ON files(sha256);
CREATE INDEX idx_files_status ON files(status);
CREATE INDEX idx_files_created_at ON files(created_at DESC);

-- Chunks table: stores text chunks from PDFs
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL UNIQUE,  -- file_id__chunk_index format
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    token_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for chunks
CREATE INDEX idx_chunks_file_id ON chunks(file_id);
CREATE INDEX idx_chunks_chunk_id ON chunks(chunk_id);
CREATE INDEX idx_chunks_chunk_index ON chunks(file_id, chunk_index);

-- Summaries table: stores per-chunk summaries
CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL REFERENCES chunks(chunk_id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    summary_text TEXT NOT NULL,
    llm_provider TEXT,
    llm_model TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for summaries
CREATE INDEX idx_summaries_file_id ON summaries(file_id);
CREATE INDEX idx_summaries_chunk_id ON summaries(chunk_id);

-- Notes table: stores final synthesized notes
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES files(id) ON DELETE CASCADE UNIQUE,
    note_text TEXT NOT NULL,
    metadata JSONB,  -- store additional info like total_chunks, synthesis_method, etc.
    llm_provider TEXT,
    llm_model TEXT,
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for notes
CREATE INDEX idx_notes_file_id ON notes(file_id);

-- Enable Row Level Security (RLS) - optional, configure based on your needs
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Example RLS policy: allow all operations for authenticated users
-- Modify these based on your authentication requirements
CREATE POLICY "Allow all for authenticated users" ON files
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all for authenticated users" ON chunks
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all for authenticated users" ON summaries
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all for authenticated users" ON notes
    FOR ALL USING (auth.role() = 'authenticated');
