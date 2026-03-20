import os
import PyPDF2
import json
import time
from pathlib import Path

# from openai import OpenAI  ## if using OpenAI's official library
from dotenv import load_dotenv
import requests

from prompts import get_rule_extraction_prompt


PDF_FILE = "DC_EGD09106A1_Overall.pdf"
#  OUTPUT_FILE = "summaries.json" ## if saving summaries
OUTPUT_FILE = "rules.json"

# Skip the front content/index pages
SKIP_FIRST_PAGES = 24

# Keep this small for testing first
MAX_CHUNKS_TO_PROCESS = 3

# Approx chunk size in characters
CHUNK_SIZE = 12000


def extract_pdf_text(pdf_path: str, skip_first_pages: int = 0) -> str:
    text_parts = []

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        total_pages = len(reader.pages)
        print(f"Total pages in PDF: {total_pages}")

        for i, page in enumerate(reader.pages):
            page_number = i + 1

            if i < skip_first_pages:
                print(f"Skipping page {page_number}")
                continue

            try:
                page_text = page.extract_text()
            except Exception as e:
                print(f"Could not extract page {page_number}: {e}")
                continue

            if page_text and page_text.strip():
                cleaned_text = f"\n--- PAGE {page_number} ---\n{page_text.strip()}\n"
                text_parts.append(cleaned_text)

    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 12000) -> list[str]:
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        if end < text_length:
            split_index = text.rfind("\n", start, end)
            if split_index > start:
                end = split_index

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end

    return chunks


# def summarize_chunk(client: OpenAI, chunk: str, chunk_number: int) -> str:
#    prompt = get_summary_prompt(chunk, chunk_number)

#    response = client.chat.completions.create(
#        model="gpt-4o-mini",
#        messages=[
#            {
#                "role": "system",
#                "content": "You are a precise engineering document analysis assistant."
#            },
#            {
#                "role": "user",
#                "content": prompt
#            }
#        ]
#    )

#    return response.choices[0].message.content or ""     ## if using OpenAI's official library


def summarize_chunk(chunk: str, chunk_number: int):
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    prompt = get_rule_extraction_prompt(chunk, chunk_number)

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "testingAPI"
    }

    data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    for attempt in range(3):
        response = requests.post(url, headers=headers, json=data, timeout=120)

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            try:
                return json.loads(content)
            except Exception:
                print("Failed to parse JSON, raw output returned.")
                return content

        print(f"Attempt {attempt + 1} failed: {response.text}")
        time.sleep(5)

    return []

def save_json(data: list, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main() -> None:
    load_dotenv()

    # api_key = os.getenv("OPENAI_API_KEY")
    # if not api_key:
    #    raise ValueError("OPENAI_API_KEY not found in .env file")

    pdf_path = Path(PDF_FILE)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # client = OpenAI(api_key=api_key) ## if using OpenAI's official library

    print("Reading PDF...")
    full_text = extract_pdf_text(str(pdf_path), skip_first_pages=SKIP_FIRST_PAGES)

    if not full_text.strip():
        raise ValueError("No text was extracted from the PDF")

    print("Chunking text...")
    chunks = chunk_text(full_text, chunk_size=CHUNK_SIZE)

    print(f"Total chunks created: {len(chunks)}")

    if not chunks:
        raise ValueError("No chunks were created from the extracted text")

    summaries = []
    chunks_to_process = min(MAX_CHUNKS_TO_PROCESS, len(chunks))

    for i in range(chunks_to_process):
        chunk_number = i + 1
        print(f"Summarizing chunk {chunk_number}/{chunks_to_process}...")

        # summary = summarize_chunk(client, chunks[i], chunk_number) ## if using OpenAI's official library
        summary = summarize_chunk(chunks[i], chunk_number)

        summaries.append({
        "chunk_number": chunk_number,
        "rules": summary
        })

    save_json(summaries, OUTPUT_FILE)
    print(f"Done. Output saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
