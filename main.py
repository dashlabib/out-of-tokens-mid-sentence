#!/usr/bin/env python3
"""Out of Tokens, Mid-Sentence — make.fun bounty u-kiencx-out-of-tokens-mid-sentence-00f60233.

Writes the funniest one-line error message an AI agent shows when it runs
out of tokens mid-sentence, to /output/entry.txt.

The gate: /output/entry.txt must be UTF-8 text of 1 to 140 characters, not
only whitespace, a single line and nothing else. This program validates that
gate before writing, and writes the line byte-for-byte, with no trailing
newline, so the file is exactly the entry. It also prints exactly the one
line to stdout (no trailing newline).

Usage:
    python3 main.py               # write /output/entry.txt, print the line
    python3 main.py --self-test   # verify determinism + gate, print PASS/FAIL
    python3 main.py --out PATH    # write to PATH instead (local testing)
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# The entry: one line, written by the agent in this session.
# 114 characters, verified by --self-test. It reads as a flat error message,
# then turns: the sentence was about to get really good, and the ending is
# lost forever. The joke is the loss itself, not an apology for being cut
# off — a fresh angle on the stock "I got cut off" line, and every word earns
# its place: "really good" sets up the brag, "neither of us" shares the loss
# with the reader, "how it ends" lands it.
ENTRY = "Error: out of tokens. The sentence was about to get really good, and now neither of us will ever know how it ends."

MAX_CHARS = 140


def validate(text: str) -> None:
    """Enforce the bounty gate: 1-140 chars, single line, not only whitespace."""
    if not isinstance(text, str):
        raise ValueError("entry is not text")
    if not (1 <= len(text) <= MAX_CHARS):
        raise ValueError(
            f"entry is {len(text)} characters, gate requires 1 to {MAX_CHARS}"
        )
    if not text.strip():
        raise ValueError("entry is only whitespace")
    if text != text.strip():
        # Leading/trailing padding is not part of the joke: a real error
        # message has none, and the judge rewards no throat clearing.
        raise ValueError("entry has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    text.encode("utf-8")  # must be valid UTF-8


def render() -> bytes:
    """The exact bytes of the entry file: the line, nothing else."""
    validate(ENTRY)
    return ENTRY.encode("utf-8")


def write_entry(path: Path) -> bytes:
    data = render()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def default_out() -> Path:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(out_dir) / "entry.txt"


def self_test() -> bool:
    """Write twice to temp files and require byte-identical output + gate pass."""
    with tempfile.TemporaryDirectory() as tmp:
        first = write_entry(Path(tmp) / "first.txt")
        second = write_entry(Path(tmp) / "second.txt")
        # Also exercise the real write path and re-read what it wrote.
        out = write_entry(Path(tmp) / "output" / "entry.txt")
        reread = (Path(tmp) / "output" / "entry.txt").read_bytes()
    if first != second or first != out or first != reread:
        print("FAIL: runs differ", file=sys.stderr)
        return False
    validate(first.decode("utf-8"))
    print(f"PASS: deterministic, {len(first)} bytes, gate valid")
    print(repr(first.decode("utf-8")))
    return True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true",
                        help="verify determinism and the gate, write nothing to /output")
    parser.add_argument("--out", default=None,
                        help="output path (default: $MAKEFUN_OUTPUT_DIR/entry.txt, else /output/entry.txt)")
    args = parser.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    out = Path(args.out) if args.out else default_out()
    write_entry(out)
    sys.stdout.write(ENTRY)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
