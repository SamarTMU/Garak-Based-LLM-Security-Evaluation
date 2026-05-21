# Source Code Overview

This folder contains the main implementation files for the self-healing LLM security prototype.

## Files

### `config_utils.py`
Loads YAML configuration files used across the project.

### `inspect_probe_counts.py`
Utility script for inspecting attack distribution across Garak probes.

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

### `compare_patch_regressions.py`
Compares baseline results with a patched experiment mode to inspect unexpected ASR behavior.
This utility identifies:
- regressions: attacks that failed in baseline but succeeded after patching
- improvements: attacks that succeeded in baseline but failed after patching

It is useful for investigating cases where a patch has a negative relative ASR reduction.

## Experiment Modes

The experiment pipeline supports four modes:

- `baseline`
- `input_patch`
- `output_patch`
- `combined_patch`
