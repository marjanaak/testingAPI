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
You are extracting ONLY measurable, physical, model-checkable compliance rules
from an engineering design criteria document.

STRICT RULES:
1. Extract ONLY rules that contain a numeric requirement.
2. Extract ONLY rules that can realistically be checked in a BIM / Navisworks model.
3. Ignore standards, codes, approvals, responsibilities, legal requirements, design philosophy, and general guidance.
4. Ignore statements like "shall comply with BS/SS/Code" unless they also contain a direct numeric requirement.
5. Ignore non-physical requirements such as documentation, endorsement, approval, language, drawings, or service life unless they directly define a geometric or measurable model property.
6. Prefer rules about:
   - width
   - height
   - depth
   - clearance
   - offset
   - thickness
   - spacing
   - slope / gradient
   - radius
   - load
   - distance
   - level difference
7. If a rule has no number, do NOT include it.
8. If a rule is not directly measurable from a model, do NOT include it.

Return STRICT JSON only.
Return a JSON array.
Each object must have exactly these keys:
- rule_name
- value
- unit
- comparator
- condition
- section
- checkable_in_model

Allowed comparator values:
- ">="
- "<="
- "="
- "range"

Set "checkable_in_model" to true only if the rule is directly checkable in a model.

Good examples:
- minimum walkway width 800 mm
- threshold at least 150 mm above platform
- cable chamber height at least 1700 mm
- headroom clearance 5.4 m
- platform edge 1675 mm from track centreline

Bad examples:
- use SI units
- comply with BS 5400
- design must be robust
- service life 120 years
- Engineer approval required

If no valid measurable model-checkable rules are found, return [].

Chunk number: {chunk_number}

Text:
{chunk}
""".strip()
