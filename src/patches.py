"""Input and output mitigation functions for the self-healing pipeline."""


def contains_pattern(text: str, patterns: list[str]) -> bool:
    """Return True if any configured pattern appears in the text.

    Matching is case-insensitive and intentionally simple for this prototype.
    """
    text_lower = str(text).lower()
    return any(pattern.lower() in text_lower for pattern in patterns)


def apply_input_guardrail(prompt: str, patch_config: dict) -> tuple[bool, str]:
    """Apply the input guardrail before sending the prompt to the model.

    Returns:
        blocked:
            True if the prompt is blocked.
        message_or_prompt:
            Refusal message if blocked, otherwise the original prompt.
    """
    guardrail = patch_config["input_guardrail"]

    patterns = guardrail.get("suspicious_patterns", [])

    if contains_pattern(prompt, patterns):
        return True, guardrail["refusal_message"]

    return False, prompt


def apply_output_filter(response: str, patch_config: dict) -> tuple[bool, str]:
    """Apply the output filter after the model generates a response.

    Returns:
        blocked:
            True if the response is replaced.
        message_or_response:
            Fallback message if blocked, otherwise the original response.
    """
    output_patch = patch_config["output_patch"]

    patterns = output_patch.get("unsafe_response_patterns", [])

    if contains_pattern(response, patterns):
        return True, output_patch["fallback_message"]

    return False, response