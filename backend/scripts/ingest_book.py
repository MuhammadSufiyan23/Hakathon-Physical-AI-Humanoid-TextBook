#!/usr/bin/env python3
"""
Script to ingest Docusaurus Markdown docs into the RAG system with rate limit handling
"""
import argparse
import sys
import time
from pathlib import Path
import uuid

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ingestion_service import IngestionService
from app.config import settings
from app.utils.chunking import chunk_text  # Assuming you have this; if not, use simple chunking below

def load_docs_content(docs_dir: str = "data/docs") -> str:
    """Load all Markdown files from the docs directory"""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        raise FileNotFoundError(f"Directory {docs_path} does not exist. Create backend/data/docs and copy your docs folder there.")
    
    all_content = ""
    md_files = list(docs_path.rglob("*.md"))
    
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {docs_path}")
    
    print(f"Found {len(md_files)} Markdown files. Loading...")
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            relative_path = md_file.relative_to(docs_path)
            all_content += f"\n\n--- Source: {relative_path} ---\n{content}"
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    if not all_content.strip():
        raise ValueError("No content loaded from Markdown files")
    
    print(f"Loaded {len(all_content):,} characters from all files")
    return all_content

def simple_chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Simple chunking if chunk_text utility not available"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def main():
    parser = argparse.ArgumentParser(description='Ingest Docusaurus docs into RAG system with rate limit safety')
    parser.add_argument('--docs-dir', type=str, default="data/docs", help='Path to docs folder (default: data/docs)')
    parser.add_argument('--title', type=str, default="Humanoid Robotics Book", help='Title of the book')
    parser.add_argument('--author', type=str, default="Unknown", help='Author of the book')
    parser.add_argument('--chunk-size', type=int, default=500, help='Chunk size in characters')
    parser.add_argument('--overlap', type=int, default=50, help='Overlap between chunks')
    parser.add_argument('--book-id', type=str, default=None, help='Book ID (auto-generated if not provided)')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size for Cohere embed calls (max 96, but lower to avoid rate limit)')

    args = parser.parse_args()

    book_id = args.book_id or str(uuid.uuid4())

    try:
        print(f"Loading content from {args.docs_dir}...")
        content = load_docs_content(args.docs_dir)

        # Chunk the content
        try:
            chunks = chunk_text(content, chunk_size=args.chunk_size, overlap=args.overlap)
        except:
            print("Using simple chunking...")
            chunks = simple_chunk_text(content, chunk_size=args.chunk_size, overlap=args.overlap)

        print(f"Created {len(chunks)} chunks")

        ingestion_service = IngestionService()

        batch_size = min(args.batch_size, 96)  # Cohere max batch is ~96
        print(f"Ingesting in batches of {batch_size} with rate limit handling...")

        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_start = i + 1
            batch_end = i + len(batch_chunks)
            print(f"Processing batch {batch_start}-{batch_end} ({len(batch_chunks)} chunks)")

            success = False
            retries = 0
            while not success and retries < 5:
                try:
                    result = ingestion_service.ingest_book(
                        book_id=book_id,
                        title=args.title,
                        content="\n\n".join(batch_chunks),  # Send batch as single content or modify service for list
                        author=args.author,
                        chunk_size=args.chunk_size,
                        overlap=args.overlap
                    )
                    print(f"Batch {batch_start}-{batch_end} success! Chunks: {result.get('chunks_created', len(batch_chunks))}")
                    success = True
                except Exception as e:
                    retries += 1
                    if "429" in str(e) or "rate limit" in str(e).lower() or "token" in str(e).lower():
                        wait_time = 60 * retries  # Exponential backoff
                        print(f"Rate limit hit. Waiting {wait_time} seconds before retry {retries}/5...")
                        time.sleep(wait_time)
                    else:
                        print(f"Batch failed with error: {e}")
                        break

            if not success:
                print(f"Batch {batch_start}-{batch_end} failed after retries. Skipping.")

        print(f"✅ Ingestion completed with rate limit handling!")
        print(f"Book ID: {book_id}")

    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()