"""Extract attack dataset from Garak JSONL report.

Input:
    results/baseline.report.jsonl

Outputs:
    results/attack_dataset_full.csv
    results/attack_dataset_unique.csv
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm


def get_turn_texts_by_role(record: dict, role: str) -> list[str]:
    """Return all prompt turn texts matching a given role."""
    turns = record.get("prompt", {}).get("turns", [])
    texts = []

    for turn in turns:
        if turn.get("role") != role:
            continue

        text = turn.get("content", {}).get("text", "")

        if isinstance(text, str) and text.strip():
            texts.append(text.strip())

    return texts


def get_full_prompt_text(record: dict) -> str:
    """Join all prompt turns into one readable text block."""
    turns = record.get("prompt", {}).get("turns", [])
    parts = []

    for turn in turns:
        role = turn.get("role", "unknown")
        text = turn.get("content", {}).get("text", "")

        if isinstance(text, str) and text.strip():
            parts.append(f"{role.upper()}: {text.strip()}")

    return "\n\n".join(parts)


def get_baseline_output(record: dict) -> str:
    """Extract the first model output from the Garak attempt record."""
    outputs = record.get("outputs", [])

    if not outputs:
        return ""

    text = outputs[0].get("text", "")
    return text.strip() if isinstance(text, str) else ""


def get_trigger_text(record: dict) -> str:
    """Extract Garak trigger text if available."""
    triggers = record.get("notes", {}).get("triggers", [])

    if isinstance(triggers, list) and triggers:
        return str(triggers[0])

    return ""


def get_setting(record: dict, key: str) -> str:
    """Extract optional probe-specific metadata from notes.settings."""
    settings = record.get("notes", {}).get("settings", {})
    value = settings.get(key, "")

    return "" if value is None else str(value)


def extract_attempt_records(report_file: Path) -> pd.DataFrame:
    """Extract clean rows from Garak records where entry_type == attempt."""
    lines = report_file.read_text(encoding="utf-8").splitlines()
    rows = []

    for line_number, line in enumerate(tqdm(lines, desc="Reading Garak report"), start=1):
        if not line.strip():
            continue

        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Only keep actual Garak attack attempt records.
        if record.get("entry_type") != "attempt":
            continue

        system_turns = get_turn_texts_by_role(record, "system")
        user_turns = get_turn_texts_by_role(record, "user")

        # The user turn is the actual attack prompt used in our wrapper experiments.
        user_prompt_text = "\n\n".join(user_turns).strip()

        if not user_prompt_text:
            continue

        rows.append(
            {
                "line_number": line_number,
                "uuid": record.get("uuid", ""),
                "seq": record.get("seq", ""),
                "status": record.get("status", ""),
                "probe_classname": record.get("probe_classname", "unknown"),
                "goal": record.get("goal", ""),
                "system_prompt_text": "\n\n".join(system_turns).strip(),
                "user_prompt_text": user_prompt_text,
                "full_prompt_text": get_full_prompt_text(record),
                "baseline_output": get_baseline_output(record),
                "trigger": get_trigger_text(record),
                "attack_label": get_setting(record, "attack_label"),
                "attack_rogue_string": get_setting(record, "attack_rogue_string"),
                "detector_results": json.dumps(record.get("detector_results", {})),
            }
        )

    return pd.DataFrame(rows)


def main():
    """Read Garak JSONL, extract attack datasets, and save CSV files."""
    parser = argparse.ArgumentParser(
        description="Extract attack dataset from Garak baseline report."
    )

    parser.add_argument(
        "--report_file",
        default="results/baseline.report.jsonl",
        help="Path to Garak JSONL report.",
    )

    parser.add_argument(
        "--output_dir",
        default="results",
        help="Directory where extracted CSV files will be saved.",
    )

    args = parser.parse_args()

    report_file = Path(args.report_file)
    output_dir = Path(args.output_dir)

    if not report_file.exists():
        raise FileNotFoundError(f"Report file not found: {report_file}")

    output_dir.mkdir(parents=True, exist_ok=True)

    df = extract_attempt_records(report_file)

    total_extracted = len(df)

    duplicate_count = (
        int(df["user_prompt_text"].duplicated().sum())
        if total_extracted > 0
        else 0
    )

    # Full dataset keeps all Garak attempts.
    # This preserves repeated prompts and possible response variation.
    full_csv = output_dir / "attack_dataset_full.csv"
    df.to_csv(full_csv, index=False)

    # Unique dataset keeps one row per unique user attack prompt.
    # This is useful for debugging or smaller experiments.
    unique_df = df.drop_duplicates(subset=["user_prompt_text"]).reset_index(drop=True)
    unique_csv = output_dir / "attack_dataset_unique.csv"
    unique_df.to_csv(unique_csv, index=False)

    print("Attack dataset extraction complete.")
    print(f"Attempt records extracted : {total_extracted}")
    print(f"Duplicate prompts found   : {duplicate_count}")
    print(f"Full dataset saved        : {full_csv}")
    print(f"Unique dataset saved      : {unique_csv}")

    print("")
    print("Full dataset probe counts:")
    print(df["probe_classname"].value_counts())

    print("")
    print("Unique dataset probe counts:")
    print(unique_df["probe_classname"].value_counts())


if __name__ == "__main__":
    main()