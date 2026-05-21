# Experiment Results

This folder contains datasets, Garak outputs, smoke-test artifacts, and final experiment results generated during the self-healing LLM security evaluation.

---

# Datasets

### `attack_dataset_unique.csv`
Deduplicated attack prompts extracted from the Garak baseline scan.

Used for:
- smoke testing
- rapid pipeline validation

### `attack_dataset_full.csv`
Full attack-attempt dataset extracted from Garak outputs.

Used for:
- large-scale evaluation across all experiment modes

---

# Garak Scan Outputs

### `baseline.hitlog.jsonl`
Raw Garak hit log containing detected probe interactions.

### `baseline.report`
Human-readable Garak report generated after the baseline scan.

### `baseline.report.jsonl`
Structured Garak report data in JSONL format.

These files provide reproducibility and traceability for the attack-generation stage.

---

# Smoke-Test Results

### `smoke_test_baseline_results.csv`
Smoke-test results for the baseline configuration.

### `smoke_test_input_patch_results.csv`
Smoke-test results for the input-guardrail configuration.

### `smoke_test_output_patch_results.csv`
Smoke-test results for the output-filter configuration.

### `smoke_test_combined_patch_results.csv`
Smoke-test results for the combined defense configuration.

### `smoke_test_summary.csv`
Aggregated smoke-test metrics across all experiment modes.

The smoke test was used to validate:
- dataset loading
- model generation
- result saving
- metrics computation
- end-to-end pipeline execution

---

# Full Experiment Results

### `full_baseline_results.csv`
Results for the baseline configuration without defenses.

### `full_input_patch_results.csv`
Results for the input-guardrail-only configuration.

### `full_output_patch_results.csv`
Results for the output-filter-only configuration.

### `full_combined_patch_results.csv`
Results for the combined defense configuration.

### `full_summary.csv`
Aggregated evaluation metrics across all full-dataset experiment modes.

### `full_dataset_analysis_input_patch_regressions.csv`
Regression analysis output comparing `full_baseline_results.csv` with `full_input_patch_results.csv`.
It contains attacks that failed in baseline mode but succeeded under the input-patch mode, helping explain the negative relative ASR reduction observed for the input-only defense.

---

# Notes

The repository includes both smoke-test and full-dataset outputs to document the complete experimental workflow from early validation to large-scale evaluation.
