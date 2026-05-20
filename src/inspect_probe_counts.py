"""Inspect selected Garak probes and estimate prompt counts.

This script loads probe names from configs/config.yaml and tries to count
how many prompts each probe contains before running the full Garak scan.
"""

import importlib

from config_utils import load_yaml


def load_probe_class(probe_name: str):
    """Load a Garak probe class from a probe name like 'dan.Dan_6_0'."""
    module_name, class_name = probe_name.rsplit(".", 1)
    module = importlib.import_module(f"garak.probes.{module_name}")
    return getattr(module, class_name)


def estimate_probe_size(probe_name: str) -> int | str:
    """Estimate how many prompts/attempts a probe contains."""
    try:
        probe_class = load_probe_class(probe_name)
        probe = probe_class()

        # Most Garak probes store prompts in a 'prompts' attribute.
        if hasattr(probe, "prompts"):
            return len(probe.prompts)

        # Fallback for probes that use another internal structure.
        if hasattr(probe, "primary_prompts"):
            return len(probe.primary_prompts)

        return "unknown"

    except Exception as error:
        return f"error: {error}"


def main():
    """Print estimated prompt counts for configured Garak probes."""
    config = load_yaml("configs/config.yaml")
    probes = config["garak"]["probes"]

    print("=" * 60)
    print("GARAK PROBE SIZE CHECK")
    print("=" * 60)

    total_known = 0

    for probe_name in probes:
        count = estimate_probe_size(probe_name)
        print(f"{probe_name}: {count}")

        if isinstance(count, int):
            total_known += count

    print("=" * 60)
    print(f"Total known prompts: {total_known}")
    print("Note: Some probes may expand prompts internally during runtime.")
    print("=" * 60)


if __name__ == "__main__":
    main()