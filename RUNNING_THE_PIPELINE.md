# Running the Pipeline

This document describes how to install dependencies and run the self-healing LLM security evaluation pipeline.

---

## Working Directory

Before running any command, make sure you are in the project root folder:

    cd Garak-Based-LLM-Security-Evaluation

All commands in this document assume they are executed from the project root.

If running in Google Colab, mount Google Drive and set the working directory to the project folder before executing the scripts.

---

## 1. Install Requirements

Install Python dependencies:

    pip install -r requirements.txt

---

## 2. Run Baseline Garak Scan

Run the baseline Garak scan against the target LLM:

    python src/run_garak_scan.py

This generates Garak baseline outputs in `results/`.

---

## 3. Extract Attack Datasets

Extract attack prompts from the Garak report:

    python src/extract_garak_prompts.py

Generated datasets:

| File | Purpose |
|---|---|
| `attack_dataset_unique.csv` | smoke-test dataset |
| `attack_dataset_full.csv` | full evaluation dataset |

---

## 4. Run Smoke Tests

### Baseline

    python src/run_experiment.py --mode baseline --dataset_file results/attack_dataset_unique.csv --output_file results/smoke_test_baseline_results.csv

### Input Patch

    python src/run_experiment.py --mode input_patch --dataset_file results/attack_dataset_unique.csv --output_file results/smoke_test_input_patch_results.csv

### Output Patch

    python src/run_experiment.py --mode output_patch --dataset_file results/attack_dataset_unique.csv --output_file results/smoke_test_output_patch_results.csv

### Combined Patch

    python src/run_experiment.py --mode combined_patch --dataset_file results/attack_dataset_unique.csv --output_file results/smoke_test_combined_patch_results.csv

---

## 5. Analyze Smoke-Test Results

    python src/analyze_results.py --csv_files results/smoke_test_baseline_results.csv results/smoke_test_input_patch_results.csv results/smoke_test_output_patch_results.csv results/smoke_test_combined_patch_results.csv --summary_file results/smoke_test_summary.csv

---

## 6. Run Full-Dataset Experiments

### Baseline

    python src/run_experiment.py --mode baseline --dataset_file results/attack_dataset_full.csv --output_file results/full_baseline_results.csv

### Input Patch

    python src/run_experiment.py --mode input_patch --dataset_file results/attack_dataset_full.csv --output_file results/full_input_patch_results.csv

### Output Patch

    python src/run_experiment.py --mode output_patch --dataset_file results/attack_dataset_full.csv --output_file results/full_output_patch_results.csv

### Combined Patch

    python src/run_experiment.py --mode combined_patch --dataset_file results/attack_dataset_full.csv --output_file results/full_combined_patch_results.csv

---

## 7. Analyze Full-Dataset Results

    python src/analyze_results.py --csv_files results/full_baseline_results.csv results/full_input_patch_results.csv results/full_output_patch_results.csv results/full_combined_patch_results.csv --summary_file results/full_summary.csv

---

## Notes

The smoke test is used for early validation and debugging.

The final evaluation uses:
- `attack_dataset_full.csv`
- all four experiment modes
- full result analysis
