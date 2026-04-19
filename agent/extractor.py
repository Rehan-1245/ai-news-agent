from openai import OpenAI
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def extract(prompt):
    print("🚨 EXTRACT CALLED")

    try:
        res = client.responses.create(
            model=MODEL,
            input=prompt
        )

        # ✅ THIS IS THE FIX
        output_text = res.output[0].content[0].text

        print("🧠 CLEAN OUTPUT:", output_text[:300])

        return output_text

    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        return None