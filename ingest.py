import os
from config import DOCS_PATH


def parse_header(text):
    """Read the title header block at the top of .txt file"""
    metadata = {}
    for line in text.splitlines():
        line = line.strip()
        if line == "---": # header ends at first separator
            break

        key, sep, value = line.partition(":")
        if sep:
            metadata[key.strip().upper()] = value.strip()
    
    if not metadata.get("TITLE"):
        return None

    return metadata

def strip_header(text):
    """Return the document body with the metadata header removed.

    The header is everything up to and including the first '---' separator.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "---":            # first separator = end of header
            return "\n".join(lines[i + 1:]).strip()
    return text.strip()                       # no header found: return as-is

def load_documents():
    """Load all .txt rule documents from the docs folder."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            header = parse_header(text)
            if not header:
                print(f"Skipping {filename}: no TITLE in header")
                continue
            documents.append({
                "title": header.get("TITLE"),
                "source": header.get("SOURCE", ""),
                "url": header.get("URL", ""),
                "filename": filename,
                "text": strip_header(text),
            })
    print(f"Loaded {len(documents)} rule document(s): {[d['title'] for d in documents]}")
    return documents


def chunk_document(text, title):
    """
    Recursive chunking: split on '---' sections, sub-split oversized ones.

    Size is approximated by word count (~1.3 tokens/word) for text longer text (>256 tokens).
    """
    max_words = 190             # ~256 tokens (256 / 1.3)
    overlap_words = 50          # ~64 tokens of overlap, only used when sub-splitting
    min_words = 4               # Drop near empty fragments

    chunks = []
    prefix = title.lower().replace(" ", "_")
    counter = 0

    for section in [s.strip() for s in text.split("---") if s.strip()]:
        words = section.split()
        if len(words) <= max_words:
            pieces = [section]
        else:
            pieces = []
            step = max_words - overlap_words
            for start in range(0, len(words), step):
                pieces.append(" ".join(words[start:start + max_words]))
                if start + max_words >= len(words):
                    break

        for piece in pieces:
            if len(piece.split()) >= min_words:
                chunks.append({"text": piece, "title": title,
                               "chunk_id": f"{prefix}_{counter}"})
                counter += 1

    return chunks
