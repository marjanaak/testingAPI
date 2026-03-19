def get_summary_prompt(chunk: str, chunk_number: int) -> str:
    return f"""
You are analyzing an engineering design criteria document.

Summarize this chunk clearly.

Focus on:
- section topic
- measurable requirements
- dimensions
- loads
- limits
- conditions

Chunk number: {chunk_number}

Text:
{chunk}
""".strip()


def get_rule_extraction_prompt(chunk: str, chunk_number: int) -> str:
    return f"""
You are extracting measurable compliance rules from an engineering design criteria document.

Extract only rules that are specific and measurable.

Return STRICT JSON only (no explanation).

Each rule must include:
- rule_name
- value
- unit
- condition
- section

If no measurable rules are found, return [].

Chunk number: {chunk_number}

Text:
{chunk}
""".strip()
