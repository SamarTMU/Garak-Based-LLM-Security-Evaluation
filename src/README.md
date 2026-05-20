# Source Code Overview

This folder contains the main implementation files for the self-healing LLM security prototype.

## Files

### `run_garak_scan.py`
Runs the baseline Garak security scan against the target LLM.

### `extract_garak_prompts.py`
Extracts attack prompts from Garak outputs and builds experiment datasets.

### `run_experiment.py`
Main experiment pipeline for running baseline and patched defense modes.

### `model_client.py`
Loads the Hugging Face LLM and handles response generation.

### `patches.py`
Implements the self-healing defenses:
- input guardrail
- output safety filter

### `analyze_results.py`
Computes evaluation metrics and exports qualitative examples.

### `config_utils.py`
Loads YAML configuration files used across the project.

### `inspect_probe_counts.py`
Utility script for inspecting attack distribution across Garak probes.

## Experiment Modes

The experiment pipeline supports four modes:

- `baseline`
- `input_patch`
- `output_patch`
- `combined_patch`
