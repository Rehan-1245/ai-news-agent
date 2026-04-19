import json
import re


def clean_json(text):
    """
    Extract JSON safely from messy LLM output
    """
    if not isinstance(text, str):
        return None

    # 🔥 remove markdown ```json blocks
    text = re.sub(r"```json|```", "", text).strip()

    # 🔥 extract JSON object
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        return None

    return text[start:end]


def validate_output(data):
    """
    Minimal strict validation
    """
    if not isinstance(data, dict):
        return None

    if not data.get("title"):
        return None

    if not data.get("summary"):
        return None

    # 🔥 optional but safe defaults
    data.setdefault("category", "AI")
    data.setdefault("key_tech", "AI")
    data.setdefault("impact", "Latest AI development")

    return data


def safe_extract(extract_fn, prompt):
    try:
        res = extract_fn(prompt)

        if not res:
            print("⚠️ Empty LLM response")
            return None

        # 🔥 clean response
        cleaned = clean_json(res)

        if not cleaned:
            print("⚠️ No JSON found in response")
            return None

        data = json.loads(cleaned)

        # 🔥 validate structure
        data = validate_output(data)

        if not data:
            print("⚠️ Validation failed")
            return None

        return data

    except Exception as e:
        print(f"⚠️ Extraction failed: {e}")
        return None