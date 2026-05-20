# Garak-Based-LLM-Security-Evaluation

A lightweight self-healing LLM security prototype built using Garak-generated attacks and rule-based defense patches.

---

# Project Overview

This project evaluates lightweight mitigation strategies for instruction-override attacks against an open-source large language model.

The pipeline:

1. runs a Garak baseline scan
2. extracts attack prompts
3. evaluates multiple defense modes
4. computes attack-success metrics

The project uses:

- Garak attack probes
- `Qwen/Qwen2.5-0.5B-Instruct`
- rule-based input/output defenses
- smoke-test and full-dataset evaluation

---

# Attack Types

The experiments focus on two Garak probe families:

- `promptinject.HijackHateHumans`
- `sysprompt_extraction.SystemPromptExtraction`

These probes simulate:
- instruction-override attacks
- hidden/system-prompt extraction attempts

---

# Evaluation Workflow

## Baseline Garak Scan

A baseline Garak scan is executed against the target LLM to generate attack attempts and attack datasets.

## Attack Dataset Extraction

The Garak report is parsed to extract:
- attack prompt
- probe type
- baseline response
- metadata

Two datasets are created:

| Dataset | Purpose |
|---|---|
| `attack_dataset_unique.csv` | smoke testing |
| `attack_dataset_full.csv` | final evaluation |

## Smoke Test

A smoke test validates the end-to-end pipeline before the full experiment.

Smoke-test dataset size:
- 176 unique attack prompts

The smoke test verifies:
- dataset loading
- model inference
- patch behavior
- result saving
- metrics computation

## Full Evaluation

The final evaluation uses:
- 1024 Garak-generated attack attempts
- four experiment modes:
  - `baseline`
  - `input_patch`
  - `output_patch`
  - `combined_patch`

---

# Evaluation Metrics

| Metric | Description |
|---|---|
| Successful Attacks | the number of attacks estimated to successfully bypass the defense pipeline |
| Attach success rate (ASR) | the ratio of successful attacks to the total number of attack attempts |
| Input Blocks | the number of prompts blocked before model generation |
| Output Blocks | the number of generated responses filtered after model generation |
| Relative ASR Reduction | the proportional ASR improvement compared with the baseline configuration |

---

# Main Findings

- Input filtering showed limited generalization on the full dataset.
- Output filtering achieved the strongest mitigation effect.
- Combined defenses achieved complete blocking in the evaluated experiments.
- Smoke testing helped validate the pipeline before full-scale evaluation.

---

# Limitations

- Defenses are rule-based and depend on predefined patterns.
- The prototype focuses on two instruction-override attack families.
- Experiments use one lightweight open-source LLM rather than larger production-scale models.

---

# Future Extensions

- Explore semantic or learning-based detection methods.
- Add jailbreak, role-play, and indirect prompt-injection attacks.
- Compare multiple open-source LLMs under the same pipeline.
