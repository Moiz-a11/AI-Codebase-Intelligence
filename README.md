# AI Code Reviewer & Codebase Intelligence

A resume-focused RAG project where a user uploads a complete code repository and asks questions or requests code/security reviews.

## Initial goal

Upload ZIP -> extract code -> chunk -> Hugging Face embeddings -> ChromaDB -> retrieve relevant code -> Ollama/Qwen -> answer.

## Planned upgrades

- Tree-sitter AST-aware chunking
- BGE reranking
- LangGraph agents
- Semgrep security scanning
- RAGAS evaluation
- GitHub API integration
- Docker deployment

## Stack

React + Vite, FastAPI, Python, ChromaDB, Hugging Face, Tree-sitter, LangChain/LangGraph, Ollama/Qwen, Semgrep.
