# RAG Pipeline

1. Extract supported source files.
2. Parse/chunk code.
3. Generate embeddings.
4. Store vectors in ChromaDB.
5. Retrieve relevant code for a user request.
6. Optionally rerank.
7. Send context to the local LLM.
