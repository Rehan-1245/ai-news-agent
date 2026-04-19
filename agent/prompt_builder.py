def build_prompt(pdf_text, article):
    return f"""
You are an AI news extractor.

Follow these rules:
{pdf_text}

Return ONLY valid JSON in this format:

{{
  "title": "",
  "summary": "",
  "category": "",
  "key_tech": "",
  "impact": "",
  "tags": []
}}

Text:
{article}
"""