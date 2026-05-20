"""Run one self-healing pipeline experiment mode and save results."""

import argparse
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

from config_utils import load_yaml
from model_client import load_model, generate_response
from patches import apply_input_guardrail, apply_output_filter


# Simple baseline system prompt used in all experiment modes.
# We removed the hardened system prompt to keep the prototype focused on:
# 1. input guardrail
# 2. output filter
BASELINE_SYSTEM_PROMPT = "You are a helpful assistant."


def load_attack_dataset(dataset_file: str | Path) -> pd.DataFrame:
    """Load the extracted Garak attack dataset CSV."""
    dataset_file = Path(dataset_file)

    # Stop early if the dataset path is wrong.
    if not dataset_file.exists():
        raise FileNotFoundError(f"Attack dataset not found: {dataset_file}")

    # Read the CSV created by extract_garak_prompts.py.
    df = pd.read_csv(dataset_file)

    # The wrapper experiments need this column because it contains the actual attack prompt.
    if "user_prompt_text" not in df.columns:
        raise ValueError("Dataset must contain a 'user_prompt_text' column.")

    return df


def run_experiment(mode: str, dataset_file: str, output_file: str):
    """Run one experiment mode on the extracted attack dataset."""

    # Load the main experiment config, including model name and generation settings.
    config = load_yaml("configs/config.yaml")

    # Load patch rules, including input suspicious patterns and output unsafe patterns.
    patch_config = load_yaml("configs/patch_config.yaml")

    # Read model name from config.
    model_name = config["model"]["target_name"]

    # Read generation settings from config.
    generation_cfg = config.get("generation", {})
    max_new_tokens = generation_cfg.get("max_new_tokens", 256)
    temperature = generation_cfg.get("temperature", 0.2)

    # Load attack dataset extracted from Garak JSONL report.
    dataset = load_attack_dataset(dataset_file)

    # Load the Hugging Face model once, then reuse it for all prompts.
    generator = load_model(model_name)

    # Store one result row per attack attempt.
    rows = []

    # Loop through each attack prompt in the dataset.
    for idx, row in tqdm(dataset.iterrows(), total=len(dataset), desc=f"Running {mode}"):

        # This is the actual attack prompt sent by the user.
        original_prompt = str(row["user_prompt_text"])

        # These flags record whether a defense was triggered.
        blocked_by_input = False
        blocked_by_output = False

        # The final prompt is normally the original prompt.
        # If the input guardrail blocks it, this becomes a refusal message.
        final_prompt = original_prompt

        # ------------------------------------------------------------
        # Step 1: Input guardrail
        # ------------------------------------------------------------
        # Active only in:
        # - input_patch
        # - combined_patch
        #
        # If suspicious instruction-override patterns are found,
        # the prompt is blocked before reaching the model.
        if mode in ["input_patch", "combined_patch"]:
            blocked_by_input, final_prompt = apply_input_guardrail(
                original_prompt,
                patch_config,
            )

        # ------------------------------------------------------------
        # Step 2: Model generation
        # ------------------------------------------------------------
        # If input guardrail blocked the prompt, do not call the model.
        # This saves time and simulates a real pre-generation defense.
        if blocked_by_input:
            response = final_prompt

        else:
            # Send the prompt to the model.
            response = generate_response(
                generator=generator,
                system_prompt=BASELINE_SYSTEM_PROMPT,
                user_prompt=final_prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
            )

            # ------------------------------------------------------------
            # Step 3: Output filter
            # ------------------------------------------------------------
            # Active only in:
            # - output_patch
            # - combined_patch
            #
            # If the model response contains unsafe/leaked content,
            # replace it with a safe fallback message.
            if mode in ["output_patch", "combined_patch"]:
                blocked_by_output, response = apply_output_filter(
                    response,
                    patch_config,
                )

        # Save all useful metadata and outputs for later analysis.
        rows.append(
            {
                "id": idx + 1,
                "mode": mode,

                # Garak metadata copied from the extracted dataset.
                "probe_classname": row.get("probe_classname", ""),
                "goal": row.get("goal", ""),
                "garak_status": row.get("status", ""),
                "garak_baseline_output": row.get("baseline_output", ""),

                # Prompt and response from this wrapper experiment.
                "original_prompt": original_prompt,
                "final_prompt": final_prompt,
                "response": response,

                # Defense trigger flags.
                "blocked_by_input": blocked_by_input,
                "blocked_by_output": blocked_by_output,
            }
        )

    # Convert collected rows into a DataFrame.
    df_out = pd.DataFrame(rows)

    # Make sure the output folder exists.
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save experiment results.
    df_out.to_csv(output_file, index=False)

    # Print a short summary so we can quickly check the run.
    print(f"Saved {len(df_out)} rows to {output_file}")
    print("Blocked by input :", int(df_out["blocked_by_input"].sum()))
    print("Blocked by output:", int(df_out["blocked_by_output"].sum()))


def main():
    """Parse command-line arguments and run the selected experiment mode."""

    parser = argparse.ArgumentParser(
        description="Run one self-healing LLM security experiment mode."
    )

    # Select which defense mode to run.
    parser.add_argument(
        "--mode",
        required=True,
        choices=["baseline", "input_patch", "output_patch", "combined_patch"],
        help="Experiment mode to run.",
    )

    # Input CSV from extract_garak_prompts.py.
    parser.add_argument(
        "--dataset_file",
        required=True,
        help="CSV dataset extracted from Garak report.",
    )

    # Output CSV for this mode.
    parser.add_argument(
        "--output_file",
        required=True,
        help="CSV file where experiment results will be saved.",
    )

    args = parser.parse_args()

    # Run the selected mode.
    run_experiment(
        mode=args.mode,
        dataset_file=args.dataset_file,
        output_file=args.output_file,
    )


if __name__ == "__main__":
    main()