import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


class LLMService:

    def __init__(self):
        self.url = OLLAMA_URL
        self.model = MODEL_NAME

    def generate(self, question: str, context: str):

        MAX_CONTEXT_CHARS = 20000
        
        context = context[:MAX_CONTEXT_CHARS]

        prompt = f"""
You are an AI software engineering assistant.

You are analyzing a user's software repository.

Answer the user's question using the repository
context provided below.

IMPORTANT RULES:

1. Use the repository context as your primary source.
2. Do not invent files, functions, APIs, or code.
3. If the context is insufficient, clearly say so.
4. Mention relevant file names when possible.
5. Explain technical concepts clearly.
6. If you find a problem, explain why.
7. Suggest a practical improvement when appropriate.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Now provide a clear and useful answer.
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=600
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "No answer was generated."
        )