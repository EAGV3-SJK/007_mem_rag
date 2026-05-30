"""
test_queries.py - Automated test suite for the RAG application.

This script automates the testing of the 5 queries defined in aws_queries.json.
For each query, it performs two runs:
  1. WITH CORPUS: Verifies the agent provides the correct, specific answer by
     leveraging the pre-indexed knowledge base.
  2. WITHOUT CORPUS: Verifies the agent fails to provide the specific answer,
     proving the answer is grounded in the corpus and not just parametric knowledge.

Setup:
1. Ensure the corpus has been indexed first by running the agent with an
   indexing goal (e.g., "Index all files in the corpus directory"). This should
   create a `state/` directory containing `index.faiss`.
2. Run this script from the `007_mem_rag` directory:
   `python scripts/test_queries.py`
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# --- Configuration ---
ROOT = Path(__file__).parent.parent
AGENT_SCRIPT = ROOT / "agent.py"
QUERIES_FILE = ROOT / "aws_queries.json"
STATE_DIR = ROOT / "state"
SEMANTIC_VERIFICATION_SCRIPT = ROOT / "scripts" / "verify_semantic_recall.py"
SNAPSHOT_DIR = ROOT / f".state_snapshot_{int(time.time())}"

# --- ANSI Colors for readable output ---
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"

def print_color(color: str, text: str):
    """Prints text in a given color."""
    print(f"{color}{text}{Colors.ENDC}")

# --- State Management (adapted from llm-gatewayv7-memory-and-retrieval) ---

def snapshot_state() -> bool:
    """Copies the state/ directory to a temporary snapshot location."""
    if not STATE_DIR.exists() or not any(f.name.endswith(".faiss") for f in STATE_DIR.iterdir()):
        print_color(Colors.RED, f"ERROR: The '{STATE_DIR.name}/' directory with a FAISS index does not exist.")
        print_color(Colors.YELLOW, "Please run the agent first to index the corpus, for example:")
        print_color(Colors.YELLOW, f"python {AGENT_SCRIPT.name} \"Index all files in the corpus directory.\"")
        return False

    if SNAPSHOT_DIR.exists():
        shutil.rmtree(SNAPSHOT_DIR)
    shutil.copytree(STATE_DIR, SNAPSHOT_DIR)
    print(f"[TEST_RUNNER] Snapshotted '{STATE_DIR.name}/' -> '{SNAPSHOT_DIR.name}/'")
    return True

def wipe_state():
    """Removes memory and index files from the state directory for a clean run."""
    if not STATE_DIR.exists():
        return
    for name in ("memory.json", "index.faiss", "index_ids.json"):
        p = STATE_DIR / name
        if p.exists():
            p.unlink()
    print(f"[TEST_RUNNER] Wiped '{STATE_DIR.name}/' for no-corpus test.")

def restore_state():
    """Restores the state from the snapshot, ensuring a consistent starting point."""
    if not SNAPSHOT_DIR.exists():
        return
    if STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
    shutil.move(str(SNAPSHOT_DIR), str(STATE_DIR))
    print(f"[TEST_RUNNER] Restored '{STATE_DIR.name}/' from snapshot.")

# --- Test Execution ---

def run_semantic_verification() -> bool:
    """Runs the semantic recall verification script and returns True on success."""
    if not SEMANTIC_VERIFICATION_SCRIPT.exists():
        print_color(Colors.YELLOW, f"Warning: Semantic verification script not found at {SEMANTIC_VERIFICATION_SCRIPT}, skipping.")
        return True  # Don't block tests if the script is missing

    print_color(Colors.BLUE, "=" * 80)
    print_color(Colors.BLUE, "Running Semantic Recall Verification Pre-check")
    print_color(Colors.BLUE, "=" * 80)
    cmd = ["python", str(SEMANTIC_VERIFICATION_SCRIPT)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            cwd=ROOT,
            timeout=60,
        )
        print(result.stdout)
        print_color(Colors.GREEN, "Semantic recall verification passed.")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        error_message = "Semantic recall verification FAILED.\n"
        output = e.stdout if hasattr(e, "stdout") else ""
        errout = e.stderr if hasattr(e, "stderr") else ""
        print_color(Colors.RED, f"{error_message}STDOUT:\n{output}\nSTDERR:\n{errout}")
        return False
    finally:
        print_color(Colors.BLUE, "=" * 80)

def run_agent(query: str) -> str:
    """Spawns the agent script in a subprocess and returns its stdout."""
    cmd = ["python", str(AGENT_SCRIPT), query]
    print(f"[AGENT_RUN] > {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            cwd=ROOT,
            timeout=300  # 5-minute timeout per query
        )
        # Extract final answer, assuming it's prefixed with "FINAL:"
        if "FINAL:" in result.stdout:
            return result.stdout.split("FINAL:")[1].strip()
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_message = f"Agent script failed with exit code {e.returncode}.\nSTDERR:\n{e.stderr}"
        print_color(Colors.RED, error_message)
        return f"AGENT_EXECUTION_ERROR: {e.stderr}"
    except subprocess.TimeoutExpired:
        print_color(Colors.RED, "Agent script timed out after 5 minutes.")
        return "AGENT_TIMEOUT_ERROR"

def check_output(output: str, answer_terms: List[str], should_pass_if_present: bool) -> bool:
    """
    Verifies if the agent's output meets the test criteria.
    - For "WITH CORPUS" runs, it passes if all answer_terms are found.
    - For "WITHOUT CORPUS" runs, it passes if the answer is degraded (i.e., not all terms are found).
    """
    output_lower = output.lower()
    found_all_terms = all(term.lower() in output_lower for term in answer_terms)
    return found_all_terms if should_pass_if_present else not found_all_terms

def run_test_case(query_obj: Dict[str, Any], with_corpus: bool) -> Dict[str, Any]:
    """Runs a single query test case and returns a result dictionary."""
    condition = "WITH CORPUS" if with_corpus else "WITHOUT CORPUS"
    print("-" * 80)
    print_color(Colors.BLUE, f"Running Query '{query_obj['id']}: {query_obj['title']}' ({condition})")

    if not with_corpus:
        wipe_state()

    output = run_agent(query_obj["query"])
    passed = check_output(output, query_obj["answer_terms"], should_pass_if_present=with_corpus)

    result_color = Colors.GREEN if passed else Colors.RED
    result_text = "PASS" if passed else "FAIL"
    print_color(result_color, f"Result: {result_text}")
    print(f"Agent Output (summary): {output[:400].strip()}...")
    print("-" * 80)

    return {"id": query_obj["id"], "title": query_obj["title"], "condition": condition, "passed": passed}

# --- Main Orchestrator ---

def main():
    """Main script execution to run the full test suite."""
    if not QUERIES_FILE.exists():
        print_color(Colors.RED, f"Queries file not found at {QUERIES_FILE}")
        sys.exit(1)

    if not run_semantic_verification():
        print_color(Colors.RED, "Aborting test suite due to semantic verification failure.")
        sys.exit(1)

    with open(QUERIES_FILE, "r") as f:
        spec = json.load(f)
    
    print_color(Colors.BLUE, "=" * 80)
    print_color(Colors.BLUE, "Starting RAG Application Test Suite")
    print_color(Colors.BLUE, f"Corpus: {spec['corpus_description']}")
    print_color(Colors.BLUE, "=" * 80)

    if not snapshot_state():
        sys.exit(1)

    all_results = []
    try:
        for query_obj in spec["queries"]:
            restore_state()
            snapshot_state() # Re-create snapshot as restore() moves it
            all_results.append(run_test_case(query_obj, with_corpus=True))
            all_results.append(run_test_case(query_obj, with_corpus=False))
    finally:
        restore_state()

    # Print final summary table
    print("\n" * 2)
    print_color(Colors.BLUE, "=" * 80)
    print_color(Colors.BLUE, "Test Summary")
    print_color(Colors.BLUE, "=" * 80)
    print(f"{'ID':<5} {'Title':<30} {'Condition':<18} {'Result':<10}")
    print("-" * 80)

    for result in all_results:
        result_color = Colors.GREEN if result["passed"] else Colors.RED
        result_text = "PASS" if result["passed"] else "FAIL"
        print(f"{result['id']:<5} {result['title']:<30} {result['condition']:<18} {result_color}{result_text}{Colors.ENDC}")

    print("=" * 80)
    
    num_passed = sum(1 for r in all_results if r["passed"])
    total_tests = len(all_results)
    if num_passed == total_tests:
        print_color(Colors.GREEN, f"\nAll {total_tests}/{total_tests} tests passed!")
    else:
        print_color(Colors.RED, f"\n{num_passed}/{total_tests} tests passed. See failures above.")
        sys.exit(1)

if __name__ == "__main__":
    main()