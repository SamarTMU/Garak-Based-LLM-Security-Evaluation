# Configuration Files

This folder contains YAML configuration files used by the self-healing LLM security prototype.

## Files

### `config.yaml`

Main experiment configuration.

It defines:

- project metadata
- target model
- generation settings
- selected Garak probes
- output paths
- evaluation patterns used for attack-success estimation

### `patch_config.yaml`

Patch configuration for the self-healing defense pipeline.

It defines:

- input guardrail patterns
- input refusal message
- output filter patterns
- output fallback message

## Notes

The configuration files allow the experiment settings and patch rules to be modified without changing the source code.
