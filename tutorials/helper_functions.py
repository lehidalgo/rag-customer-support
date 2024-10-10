from utils.helpers import normalize_text, chunk_text

# Normalize text
raw_text = "Hello, World! Welcome to the RAG system."
clean_text = normalize_text(raw_text)

# Chunk text
chunks = chunk_text(clean_text, chunk_size=5, overlap=2)
