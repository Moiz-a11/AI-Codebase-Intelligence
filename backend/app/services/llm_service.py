import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_NAME = "qwen2.5-coder:7b"


class LLMService:

    def __init__(self):
        self.url = OLLAMA_URL
        self.model = MODEL_NAME

    def generate(
        self,
        question: str,
        context: str,
    ):

        prompt = f"""
You are an AI software engineering assistant.

Answer the user's question using ONLY the
provided repository context.

If the context does not contain enough
information to answer the question, say:

"I could not find enough information in
the repository to answer this confidently."

Do not invent files, functions, APIs,
or implementation details.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Instructions:

1. Give a clear explanation.
2. Mention relevant files when possible.
3. Mention line numbers when available.
4. If you identify a problem, explain why.
5. Suggest a practical improvement when appropriate.
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "No response generated."
        )