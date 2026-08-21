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
        review_mode: bool = False,
    ):

        # Prevent sending an unnecessarily large context
        context = context[:20000]
        if review_mode:


            prompt = f"""
You are an expert software code reviewer.

You are reviewing code from a real software repository.

Use ONLY the repository context provided below.

Do not invent code, files, functions, vulnerabilities,
or behavior that is not supported by the provided context.

Perform a practical code review.

USER REQUEST:
{question}

REPOSITORY CONTEXT:
{context}

Analyze the code for:

1. Critical bugs
2. Security vulnerabilities
3. Performance problems
4. Code quality issues
5. Maintainability problems
6. Missing error handling
7. Missing tests
8. Possible improvements

Use this exact structure:

### 🔴 Critical Issues

List serious bugs or problems.

If none are found, write:
"No critical issues found."

### 🛡 Security

Identify only security vulnerabilities that are supported
by concrete evidence in the retrieved code.

If none are found, write:
"No obvious security issues found."

### ⚡ Performance

Identify inefficient operations or performance problems.

If none are found, write:
"No significant performance issues found."

### 🟠 Code Quality

Identify readability, structure, duplication,
or maintainability problems.

### 🟢 Suggestions

Give practical improvements.

### 💡 Recommended Fix

Provide concrete recommendations or corrected code
when appropriate.

### 📚 Sources

List the exact repository files and line ranges
used for your analysis.

Example:

- `server/auth.js` — Lines 20-45
- `client/src/api.js` — Lines 10-30

Do not mention files that are not present in the context.
"""

        else:

            prompt = f"""
You are an AI software engineering assistant.

Answer the user's question using ONLY the repository
context provided below.

IMPORTANT RULES:
1. Do not invent files, functions, classes, APIs, or behavior.

2. Use the repository context as the primary source of truth.

3. Mention relevant file paths.

4. Use exact file paths from the context.

5. If the context does not contain enough information,
   clearly say so.

6. Keep the answer technically accurate and concise.

7. Never claim that the project lacks TypeScript if the
   repository contains .ts or .tsx files.

8. Never report an issue unless there is concrete evidence
   in the retrieved code.

9. Distinguish between confirmed issues and suggestions.

10. Do not make assumptions about files that were not retrieved.

11. Before reporting a code-quality issue, verify that the
    relevant code actually appears in the repository context.

12. Do not invent line numbers, functions, variables, or files.

13. Provide a Sources section containing only files that
    were actually used from the repository context.

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