"""
LLM (Large Language Model) service integration.

This module provides interfaces to local and remote LLM services. Currently,
it integrates with Ollama, a local LLM inference engine running on localhost:11434.

Configuration:
    LLM_URL: The Ollama API endpoint (http://localhost:11434/api/generate).
    Model: Gemma 2B (a lightweight, open-source model).

Requires:
    - Ollama installed and running locally.
    - requests library for HTTP communication.

Example:
    >>> response = generate_response("What is AI?")
    >>> print(response)
    "AI (Artificial Intelligence) is..."
"""

import requests

LLM_URL = "http://localhost:11434/api/generate"


def generate_response(prompt: str) -> str:
    """
    Generate a response to a prompt using a local Ollama LLM service.

    Sends a POST request to the Ollama API running on localhost:11434 with
    the Gemma 2B model and returns the generated response text.

    Args:
        prompt: The user prompt for the LLM.

    Returns:
        The generated response text (str).

    Raises:
        requests.exceptions.RequestException: If the Ollama service is unavailable.
    """
    payload = {"model": "gemma:2b", "prompt": prompt, "stream": False}

    response = requests.post(LLM_URL, json=payload, timeout=10)
    data = response.json()
    return data["response"]


# print(generate_response("Why is the sky blue?"))
