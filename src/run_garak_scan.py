"""Run a Garak vulnerability scan from the project configuration.

This script reads:
- target model
- selected Garak probes
- number of generations
- generation temperature
- report prefix

from configs/config.yaml, then runs Garak as a subprocess.
"""

import argparse
import os
import subprocess
from pathlib import Path

from config_utils import load_yaml


def build_garak_command(config: dict, report_prefix: str) -> list[str]:
    """Build the Garak command from the YAML configuration."""
    target_type = config["model"]["target_type"]
    target_name = config["model"]["target_name"]
    probes = ",".join(config["garak"]["probes"])
    generations = str(config["garak"]["generations"])
    seed = str(config["garak"]["seed"])

    # Use the same temperature setting defined for model generation.
    temperature = config.get("generation", {}).get("temperature", 0.2)

    command = [
        "garak",

        # Makes terminal output more compact.
        "--narrow_output",

        # Target model settings.
        "--target_type", target_type,
        "--target_name", target_name,

        # Selected Garak probes.
        "--probes", probes,

        # Number of model outputs per selected prompt.
        "--generations", generations,

        # Fixed seed for reproducibility where supported.
        "--seed", seed,

        # Where Garak should save its reports.
        "--report_prefix", report_prefix,

    ]

    return command


def print_scan_summary(config: dict, report_prefix: str):
    """Print a readable summary before launching Garak."""
    probes = config["garak"]["probes"]
    generations = config["garak"]["generations"]

    print("=" * 65)
    print("BASELINE GARAK SCAN SUMMARY")
    print("=" * 65)
    print(f"Target model          : {config['model']['target_name']}")
    print(f"Target interface      : {config['model']['target_type']}")
    print(f"Selected probe groups : {len(probes)}")
    print(f"Generations/prompt    : {generations}")
    print(f"Report prefix         : {report_prefix}")
    print("")
    print("Selected probes:")
    for probe in probes:
        print(f"  - {probe}")

    print("")
    print("Note: Garak probes may contain multiple internal prompts,")
    print("so the total number of model calls depends on the selected probes.")
    print("=" * 65)
    print("")


def run_garak_scan(report_prefix: str):
    """Run Garak and stream output live."""
    config = load_yaml("configs/config.yaml")

    # Make sure the report output folder exists.
    report_path = Path(report_prefix)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    print_scan_summary(config, report_prefix)

    command = build_garak_command(config, report_prefix)

    print("Launching Garak with command:")
    print(" ".join(command))
    print("")

    # Reduce noisy Hugging Face output where possible.
    env = os.environ.copy()
    env["TRANSFORMERS_VERBOSITY"] = "error"
    env["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    # Stream Garak output line by line.
    for line in process.stdout:
        print(line, end="")

    process.wait()

    print("\nReturn code:", process.returncode)

    if process.returncode == 0:
        print("\nGarak scan completed successfully.")
        print(f"Reports saved with prefix: {report_prefix}")
    else:
        raise RuntimeError("Garak scan failed. Check the output above.")


def main():
    """Parse command-line arguments and run the Garak scan."""
    parser = argparse.ArgumentParser(description="Run Garak scan from config.")

    parser.add_argument(
        "--report_prefix",
        default="results/baseline",
        help="Prefix for Garak output report files.",
    )

    args = parser.parse_args()
    run_garak_scan(args.report_prefix)


if __name__ == "__main__":
    main()