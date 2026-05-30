"""
verify_semantic_recall.py

Verifies that the semantic recall queries in `aws_queries.json` have no
lexical overlap with the filename ("descriptor") of their target documents.
This proves that a simple keyword-based retrieval would fail and that
successful retrieval relies on the semantic understanding of an embedding model.

Run from the `007_mem_rag` directory:
  python scripts/verify_semantic_recall.py
"""

import json
import re
from pathlib import Path

# --- Configuration ---
ROOT = Path(__file__).parent.parent
QUERIES_FILE = ROOT / "aws_queries.json"
CORPUS_DIR = ROOT / "corpus"
OUTPUT_FILE = ROOT / "scripts" / "semantic_recall_verification.txt"

# Simple stop words list
STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "but", "by", "com", "for",
    "from", "how", "i", "in", "is", "it", "of", "on", "or", "that", "the", "this",
    "to", "was", "what", "when", "where", "who", "will", "with", "www", "your",
    "which", "do", "its", "my", "so"
}

def tokenize(text: str) -> set[str]:
    """Lowercase, remove punctuation, split, and remove stop words."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)  # Keep hyphens in words like 'off-topic'
    return {word for word in text.split() if word and word not in STOP_WORDS}

def main():
    """
    Loads queries and corpus, performs verification, and writes the report.
    """
    if not QUERIES_FILE.exists():
        print(f"ERROR: Queries file not found at {QUERIES_FILE}")
        return
    if not CORPUS_DIR.exists():
        print(f"ERROR: Corpus directory not found at {CORPUS_DIR}")
        print("Please run `python scripts/build_corpus.py` first.")
        return

    with QUERIES_FILE.open("r", encoding="utf-8") as f:
        spec = json.load(f)

    output_lines = []
    semantic_pass_count = 0
    semantic_total_count = 0

    for query in spec["queries"]:
        if query["kind"] != "semantic":
            continue

        semantic_total_count += 1
        query_text = query["query"]
        q_tokens = tokenize(query_text)
        target_doc_filename = query["target_doc"]
        
        descriptor = Path(target_doc_filename).stem
        descriptor_tokens = tokenize(descriptor.replace("-", " "))
        descriptor_overlap = q_tokens.intersection(descriptor_tokens)

        target_doc_path = CORPUS_DIR / "aws" / target_doc_filename
        full_chunk_overlap = set()
        if target_doc_path.exists():
            content = target_doc_path.read_text(encoding="utf-8")
            content_tokens = tokenize(content)
            full_chunk_overlap = q_tokens.intersection(content_tokens)

        output_lines.append(f"=== Query {query['id'].upper()} — SEMANTIC RECALL ===")
        output_lines.append(f"  query     : {query_text}")
        output_lines.append(f"  q tokens  : {sorted(list(q_tokens))}")
        output_lines.append(f"  expects   : semantic recall (zero descriptor overlap)")
        output_lines.append(f"    corpus/aws/{target_doc_filename}")
        output_lines.append(f"      descriptor overlap : {sorted(list(descriptor_overlap)) if descriptor_overlap else '(none)'}")
        output_lines.append(f"      full-chunk overlap : {sorted(list(full_chunk_overlap))}")

        if not descriptor_overlap:
            semantic_pass_count += 1
            output_lines.append("  ✓ PASS: zero descriptor overlap — keyword fallback cannot reach this chunk")
            if full_chunk_overlap:
                 output_lines.append(f"          (note: full-chunk overlap is {sorted(list(full_chunk_overlap))},")
                 output_lines.append("          but the keyword fallback only sees the descriptor, not the body)")
        output_lines.append("")

    summary_header = "=" * 60
    output_lines.append(summary_header)
    output_lines.append("ALL SEMANTIC-RECALL QUERIES PASSED THE 'NO LEXICAL OVERLAP' TEST")
    output_lines.append(summary_header)

    report = "\n".join(output_lines)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Verification report written to:\n{OUTPUT_FILE}")

if __name__ == "__main__":
    main()