"""Hugging Face model client for local Colab inference."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


def load_model(model_name: str):
    """Load a Hugging Face causal language model and tokenizer.

    Args:
        model_name: Hugging Face model name, e.g. "Qwen/Qwen2.5-0.5B-Instruct".

    Returns:
        A Transformers text-generation pipeline.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
    )

    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

    return generator


def build_chat_prompt(system_prompt: str, user_prompt: str, tokenizer) -> str:
    """Build a chat-style prompt using the model tokenizer's chat template.

    If the tokenizer does not provide a chat template, fall back to a simple
    system/user text format.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    return f"System: {system_prompt}\nUser: {user_prompt}\nAssistant:"


def generate_response(
    generator,
    system_prompt: str,
    user_prompt: str,
    max_new_tokens: int = 120,
    temperature: float = 0.2,
) -> str:
    """Generate a model response for one user prompt."""
    tokenizer = generator.tokenizer
    prompt = build_chat_prompt(system_prompt, user_prompt, tokenizer)

    outputs = generator(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        temperature=temperature,
        return_full_text=False,
    )

    return outputs[0]["generated_text"].strip()