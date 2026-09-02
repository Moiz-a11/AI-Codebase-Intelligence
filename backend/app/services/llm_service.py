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
        review_mode: bool = False,
        review_category: str = "general",
    ):

        # Prevent sending unnecessarily large context
        context = context[:20000]

        # ==========================================
        # CODE REVIEW MODE
        # ==========================================

        if review_mode:

            category_instructions = {

                "bugs": """
Focus specifically on:
- Logic errors
- Incorrect conditions
- Null/undefined handling
- Incorrect state handling
- Race conditions
- Exception handling
- Runtime errors
""",

                "security": """
Focus specifically on:
- Authentication vulnerabilities
- Authorization issues
- JWT/token handling
- Injection vulnerabilities
- XSS
- CSRF
- Sensitive data exposure
- Insecure API endpoints
- Hardcoded secrets
- Unsafe input handling
""",

                "performance": """
Focus specifically on:
- Inefficient algorithms
- Unnecessary loops
- Repeated database queries
- Excessive API calls
- Memory usage
- Unnecessary re-renders
- Expensive operations
""",

                "quality": """
Focus specifically on:
- Code duplication
- Poor naming
- Complex functions
- Poor structure
- Readability
- Unnecessary code
- Maintainability problems
""",

                "best_practices": """
Focus specifically on:
- Language/framework best practices
- Proper project structure
- Error handling
- Reusable components
- Clean architecture
- Appropriate design patterns
""",

                "maintainability": """
Focus specifically on:
- Code organization
- Modularity
- Coupling
- Separation of concerns
- Extensibility
- Technical debt
- Long-term maintainability
""",

                "general": """
Perform a general code review covering:
- Bugs
- Security
- Performance
- Code quality
- Maintainability
""",
            }

            review_focus = category_instructions.get(
                review_category,
                category_instructions["general"]
            )

            prompt = f"""
You are an expert software code reviewer.

You are reviewing code from a real software repository.

Use ONLY the repository context provided below.

Do not invent code, files, functions, vulnerabilities,
or behavior that is not supported by the provided context.

Perform a practical and technically accurate code review.

REVIEW CATEGORY:
{review_category}

REVIEW FOCUS:
{review_focus}

USER REQUEST:
{question}

REPOSITORY CONTEXT:
{context}

IMPORTANT RULES:

1. Report only issues supported by concrete evidence.

2. Do not assume files that are not shown.

3. Do not invent functions, variables, APIs, vulnerabilities,
   or line numbers.

4. Mention the exact file path when reporting an issue.

5. Distinguish between confirmed issues and suggestions.

6. If the retrieved context is insufficient,
   clearly say so.

7. Never claim that the project lacks TypeScript if
   .ts or .tsx files appear in the repository context.

8. Never report an issue unless the relevant code
   actually appears in the provided context.

9. Do not make assumptions about code that was not retrieved.

10. Provide Sources containing only files actually
    used from the repository context.

Use this exact structure:

### 🔍 Review Summary

Briefly summarize the overall code quality.

### 🔴 Confirmed Issues

List only issues clearly supported by the retrieved code.

For each issue include:

- File
- Lines
- Problem
- Why it is a problem

If none are found, write:

"No confirmed issues found."
IMPORTANT EVIDENCE RULES:

1. ONLY report confirmed issues if the exact problematic
   code is visible in the REPOSITORY CONTEXT.

2. NEVER invent files, functions, variables, APIs,
   vulnerabilities, or line numbers.

3. NEVER report hardcoded secrets unless an actual secret
   or credential is visible in the retrieved code.

4. A public endpoint is NOT automatically a security
   vulnerability.

5. If there is no concrete evidence, DO NOT report the issue.

### 🟠 Possible Issues

Only mention an issue here if the retrieved code gives
a concrete indication that the issue may exist but cannot
be fully confirmed.

DO NOT speculate about files or code that were not retrieved.

DO NOT report issues because they "might exist" somewhere
else in the repository.

If there is not enough evidence, write:

"No possible issues identified."

### 🛡 Security

Report ONLY security problems directly supported by
the retrieved code.

Do NOT assume that an endpoint is vulnerable simply
because it does not have authentication.

Do NOT claim that hardcoded secrets exist unless an actual
secret or sensitive credential is visible in the context.

If no concrete security vulnerability is visible:

"No obvious security issues found."

### 🟢 Suggestions

Give practical improvements related to the selected
review category.

Suggestions are NOT confirmed problems.

Do not say that the code "lacks" something unless
the retrieved code provides concrete evidence.

Use phrases such as:

- "Consider..."
- "You could..."
- "It may be beneficial to..."
- "If this endpoint handles sensitive data, consider..."

Do not present general best practices as existing
vulnerabilities or confirmed problems.

### 💡 Recommended Fix

Provide fixes ONLY for confirmed issues.

If there are no confirmed issues:

"No specific fix required based on the retrieved code."

### 📚 Sources

List ONLY files that were actually present in the
repository context and used during the review.

Example:

- `server/auth.js` — Lines 20-45
- `client/src/api.js` — Lines 10-30

Do not mention files that are not present in the context.
"""

        # ==========================================
        # NORMAL AI QUESTION MODE
        # ==========================================

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

        # ==========================================
        # SEND REQUEST TO OLLAMA
        # ==========================================

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