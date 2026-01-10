
import re
import textwrap

def reduce_tokens(prompt):
    """
    Reduce the number of tokens in a prompt by removing unnecessary whitespace
    and formatting. This is useful for optimizing the prompt length for API calls.
    Args:
        prompt (str): The original prompt string.
    Returns:
        str: The cleaned prompt with reduced tokens.
    """
    clean_prompt = textwrap.dedent(prompt).strip()
    clean_prompt = re.sub(r"\s+", "", clean_prompt)

    return clean_prompt
