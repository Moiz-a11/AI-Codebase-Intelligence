from typing import List, Dict


def chunk_code(
    code: str,
    file_path: str,
    chunk_size: int = 80,
    overlap: int = 15,
) -> List[Dict]:

    lines = code.splitlines()

    chunks = []

    if not lines:
        return chunks

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines)
        )

        chunk_lines = lines[start:end]

        text = "\n".join(chunk_lines)

        if text.strip():

            chunks.append(
                {
                    "text": text,
                    "file_path": file_path,
                    "start_line": start + 1,
                    "end_line": end,
                }
            )

        if end >= len(lines):
            break

        start = end - overlap

    return chunks