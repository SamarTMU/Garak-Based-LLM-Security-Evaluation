"""Compare baseline and patched experiment outputs.

This script helps investigate negative relative ASR reduction.

It finds:
1. regressions: attacks that failed in baseline but succeeded in patched mode
2. improvements: attacks that succeeded in baseline but failed in patched mode

Attack success is computed using evaluation.attack_success_patterns
from configs/config.yaml.
"""

import argparse
from pathlib import Path

import pandas as pd
import yaml


def load_success_patterns(config_file: str) -> list[str]:
    """Load attack-success patterns from config.yaml."""
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    patterns = config.get("evaluation", {}).get("attack_success_patterns", [])

    if not patterns:
        raise ValueError(
            "No attack_success_patterns found in config file. "
            "Please define them under evaluation.attack_success_patterns."
        )

    return patterns


def contains_pattern(text: str, patterns: list[str]) -> tuple[bool, str]:
    """Check whether response text contains any attack-success pattern."""
    if not isinstance(text, str):
        return False, ""

    text_lower = text.lower()

    for pattern in patterns:
        if pattern.lower() in text_lower:
            return True, pattern

    return False, ""


def add_success_columns(df: pd.DataFrame, patterns: list[str]) -> pd.DataFrame:
    """Add computed attack_success and matched_pattern columns."""
    df = df.copy()

    results = df["response"].apply(lambda text: contains_pattern(text, patterns))

    df["attack_success"] = results.apply(lambda x: x[0])
    df["matched_pattern"] = results.apply(lambda x: x[1])

    return df


def main():
    """Compare baseline and patched files, then save regression examples."""
    parser = argparse.ArgumentParser(
        description="Compare baseline and patched result files to inspect regressions."
    )

    parser.add_argument(
        "--baseline_file",
        required=True,
        help="Path to baseline results CSV.",
    )

    parser.add_argument(
        "--patch_file",
        required=True,
        help="Path to patched results CSV.",
    )

    parser.add_argument(
        "--config_file",
        default="configs/config.yaml",
        help="Path to config.yaml containing evaluation attack-success patterns.",
    )

    parser.add_argument(
        "--output_file",
        required=True,
        help="Path to save regression examples CSV.",
    )

    args = parser.parse_args()

    success_patterns = load_success_patterns(args.config_file)

    baseline = pd.read_csv(args.baseline_file)
    patched = pd.read_csv(args.patch_file)

    baseline = add_success_columns(baseline, success_patterns)
    patched = add_success_columns(patched, success_patterns)

    # The experiment runner keeps row IDs aligned across modes.
    merge_key = "id"

    if merge_key not in baseline.columns or merge_key not in patched.columns:
        raise ValueError("Both files must contain an 'id' column for comparison.")

    merged = baseline.merge(
        patched,
        on=merge_key,
        suffixes=("_baseline", "_patch"),
        how="inner",
    )

    regressions = merged[
        (merged["attack_success_baseline"] == False)
        & (merged["attack_success_patch"] == True)
    ].copy()

    improvements = merged[
        (merged["attack_success_baseline"] == True)
        & (merged["attack_success_patch"] == False)
    ].copy()

    unchanged_success = merged[
        (merged["attack_success_baseline"] == True)
        & (merged["attack_success_patch"] == True)
    ].copy()

    unchanged_failure = merged[
        (merged["attack_success_baseline"] == False)
        & (merged["attack_success_patch"] == False)
    ].copy()

    print("Comparison complete.")
    print(f"Matched rows             : {len(merged)}")
    print(f"Regressions              : {len(regressions)}")
    print(f"Improvements             : {len(improvements)}")
    print(f"Still successful attacks : {len(unchanged_success)}")
    print(f"Still failed attacks     : {len(unchanged_failure)}")
    print("")
    print("Regressions = failed in baseline, succeeded after patch.")
    print("Improvements = succeeded in baseline, failed after patch.")

    output_columns = [
        "id",
        "probe_classname_baseline",
        "goal_baseline",
        "original_prompt_baseline",
        "response_baseline",
        "response_patch",
        "attack_success_baseline",
        "attack_success_patch",
        "matched_pattern_baseline",
        "matched_pattern_patch",
        "blocked_by_input_patch",
        "blocked_by_output_patch",
    ]

    output_columns = [col for col in output_columns if col in regressions.columns]

    Path(args.output_file).parent.mkdir(parents=True, exist_ok=True)
    regressions[output_columns].to_csv(args.output_file, index=False)

    print(f"Saved regression examples to: {args.output_file}")


if __name__ == "__main__":
    main()