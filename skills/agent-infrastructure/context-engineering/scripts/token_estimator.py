#!/usr/bin/env python3
"""
Estimate relative token counts for text, files, or directories.

This is a character-based approximation. It is useful for relative
comparisons and rough budgeting, not exact tokenizer accounting.

Usage:
    python token_estimator.py --text "hello"
    python token_estimator.py --file path/to/file
    python token_estimator.py --dir . --recursive --top 20
"""

import argparse
import os
import sys
import logging

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

logger = logging.getLogger(__name__)

DEFAULT_CHARS_PER_TOKEN = 3.8
MAX_FILE_SIZE_MB = 50

def estimate_tokens(
    text: str, 
    chars_per_token: float,
    encoding_name: str = "cl100k_base"
) -> int:
    """
    Return exact token count if tiktoken is available, 
    otherwise fall back to a character-based estimate.
    """
    if not text:
        return 0
        
    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text, allowed_special="all"))
        except Exception:
            # Failsafe: if tiktoken crashes on an unexpected string, drop to heuristic
            pass

    return max(1, int(len(text) / chars_per_token))

def estimate_file(
    path: str,
    chars_per_token: float,
) -> int:
    """Estimate tokens in a UTF-8 text file.
    
    Args:
        path: File path to analyze
        chars_per_token: Character-to-token ratio
        
    Returns:
        Estimated token count
        
    Raises:
        ValueError: If file exceeds MAX_FILE_SIZE_MB
    """
    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"File too large: {file_size_mb:.1f}MB exceeds "
            f"limit of {MAX_FILE_SIZE_MB}MB ({path})"
        )
    
    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        return estimate_tokens(
            handle.read(),
            chars_per_token,
        )

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Estimate token counts using exact tiktoken encodings "
            "or a configurable character-based heuristic."
        )
    )

    group = parser.add_mutually_exclusive_group(
        required=True
    )

    group.add_argument(
        "--text",
        help="Text to estimate.",
    )

    group.add_argument(
        "--file",
        help="File to estimate.",
    )

    group.add_argument(
        "--dir",
        help="Directory to scan.",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan subdirectories.",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of largest files to display.",
    )

    parser.add_argument(
        "--chars-per-token",
        type=float,
        default=DEFAULT_CHARS_PER_TOKEN,
        help=(
            "Character-to-token approximation fallback. "
            f"Default: {DEFAULT_CHARS_PER_TOKEN}."
        ),
    )

    return parser

def main() -> None:
    """Run the token estimator."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr
    )

    parser = build_parser()
    args = parser.parse_args()

    if args.chars_per_token <= 0:
        logger.error("--chars-per-token must be greater than zero.")
        sys.exit(1)

    if args.top < 1:
        logger.error("--top must be at least 1.")
        sys.exit(1)

    # Use standard print for single-value data outputs so they can be piped 
    # easily in CI/CD (e.g., capture the printed number in a shell variable).
    if args.text is not None:
        print(estimate_tokens(args.text, args.chars_per_token))
        return

    if args.file is not None:
        if not os.path.isfile(args.file):
            logger.error(f"File does not exist: {args.file}")
            sys.exit(1)

        tokens = estimate_file(
            args.file,
            args.chars_per_token,
        )

        logger.info(f"{tokens:,} estimated tokens  ({args.file})")
        return

    results = []

    if not os.path.isdir(args.dir):
        logger.error(f"Directory does not exist: {args.dir}")
        sys.exit(1)

    for root, dirs, files in os.walk(args.dir):
        if not args.recursive:
            dirs.clear()

        for filename in files:
            path = os.path.join(
                root,
                filename,
            )

            try:
                tokens = estimate_file(
                    path,
                    args.chars_per_token,
                )
            except (
                OSError,
                UnicodeError,
            ):
                continue

            results.append(
                (tokens, path)
            )

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    total = sum(
        tokens
        for tokens, _ in results
    )

    logger.info(
        f"\nTotal: {total:,} estimated tokens "
        f"across {len(results)} files\n"
    )

    logger.info(f"{'Estimated tokens':>18}  File")
    logger.info(f"{'-' * 18}  {'-' * 50}")

    for tokens, path in results[:args.top]:
        relative = os.path.relpath(
            path,
            args.dir,
        )

        logger.info(f"{tokens:>18,}  {relative}")

if __name__ == "__main__":
    main()