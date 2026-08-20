import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


class LLMService:

    def __init__(self):
        self.url = OLLAMA_URL
        self.model = MODEL_NAME

    def generate(self, question: str, context: str):

       import requests


class LLMService:

    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "qwen2.5-coder:7b"

    def generate(
        self,
        question: str,
        context: str,
    ):

        # Prevent sending an unnecessarily large context
        context = context[:20000]

        prompt = f"""
You are an AI software engineering assistant.

Answer the user's question using ONLY the repository
context provided below.

IMPORTANT RULES:

1. Do not invent files, functions, classes, APIs, or behavior.
2. Use the repository context as the primary source of truth.
3. When explaining something, mention the relevant file path.
4. Use the exact file paths provided in the context.
5. If the repository context does not contain enough information,
   clearly say that the information was not found.
6. Keep the answer technically accurate and concise.
7. At the end, provide a Sources section.
8. In the Sources section, include only files that actually appear
   in the provided repository context.
9. Include line numbers when they are available.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

ANSWER FORMAT:

### Explanation

Explain the answer clearly.

### How It Works

Explain the important flow step-by-step.

### Sources

- `file/path` — Lines X-Y
- `file/path` — Lines X-Y
"""

        try:

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
                timeout=600,
            )

            response.raise_for_status()

            data = response.json()

            return data.get(
                "response",
                "No answer generated.",
            )

        except requests.exceptions.Timeout:

            return (
                "The AI model took too long to respond. "
                "Please try a smaller question."
            )

        except requests.exceptions.ConnectionError:

            return (
                "Unable to connect to Ollama. "
                "Please make sure Ollama is running."
            )

        except Exception as error:

            print(f"LLM error: {error}")

            return (
                "An error occurred while generating "
                "the AI response."
            )