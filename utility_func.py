
import re
import textwrap

def reduce_tokens(prompt):
    clean_prompt = textwrap.dedent(prompt).strip()
    clean_prompt = re.sub(r"\s+", "", clean_prompt)

    return clean_prompt