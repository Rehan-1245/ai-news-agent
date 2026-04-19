# 🔹 Core services
from services.pdf_reader import read_pdf
from services.webhook import send
from services.deduplicator import load, save

# 🔹 Scraper
from scraper.parser import parse_text
from scraper.source import get_ai_news_urls

# 🔹 Agent
from agent.prompt_builder import build_prompt
from agent import extractor

from datetime import datetime
import json
from difflib import SequenceMatcher


# 🔹 Title similarity check
def is_similar_title(t1, t2, threshold=0.8):
    if not t1 or not t2:
        return False
    return SequenceMatcher(None, t1.lower(), t2.lower()).ratio() > threshold


# 🔹 Date formatter
def format_date(dt):
    if not dt:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        return dt.strftime("%Y-%m-%d")
    except:
        return str(dt)


def run():
    print("🚀 Agent started...")

    pdf_text = read_pdf("data/rules.pdf")

    visited = load()

    # 🔥 keep only last 50 URLs
    if isinstance(visited, list):
        visited = set(visited[-50:])
    elif isinstance(visited, set):
        visited = set(list(visited)[-50:])
    else:
        visited = set()

    visited_titles = set()

    stored = None
    selected_url = ""
    selected_date = None
    fallback_text = ""

    news_list = get_ai_news_urls()

    if not news_list:
        print("❌ No AI news found")
        return

    print(f"📰 Found {len(news_list)} ranked articles")

    skipped_all = True  # 🔥 TRACK

    for item in news_list:

        url = item.get("link")
        title = item.get("title", "")
        published_date = item.get("date")

        if not url:
            continue

        # 🔥 URL dedup
        if url in visited:
            print(f"⏭️ Skipped URL: {url}")
            continue
        else:
            skipped_all = False

        # 🔥 TITLE similarity dedup
        if any(is_similar_title(title, t) for t in visited_titles):
            print(f"⏭️ Skipped similar title: {title}")
            continue

        print(f"🌐 Trying: {url}")

        try:
            article = parse_text(url) or ""
            print(f"📄 Article length: {len(article)}")
        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            continue

        if not article:
            print("⚠️ Empty article, using title")
            article = title

        article = f"{title}\n\n{article}"[:5000]
        fallback_text = article

        try:
            print("🚨 CALLING EXTRACTOR...")

            prompt = build_prompt(pdf_text, article)
            raw = extractor.extract(prompt)

            print("🧠 RAW OUTPUT:", raw[:200] if raw else "None")

            if not raw:
                continue

            start = raw.find("{")
            end = raw.rfind("}") + 1

            if start == -1 or end == -1:
                continue

            data = json.loads(raw[start:end])

            if not data.get("title"):
                continue

        except Exception as e:
            print(f"❌ Extraction/parse error: {e}")
            continue

        # ✅ SUCCESS
        stored = data
        selected_url = url
        selected_date = published_date

        visited.add(url)
        visited_titles.add(title)

        print(f"✅ Success: {data.get('title')}")
        break

    # 🔥 FORCE REPROCESS IF ALL SKIPPED
    if skipped_all and news_list:
        print("♻️ All skipped → forcing best article")

        item = news_list[0]
        selected_url = item.get("link", "")
        selected_date = item.get("date")
        title = item.get("title", "")

        try:
            article = parse_text(selected_url) or title
            article = f"{title}\n\n{article}"[:5000]

            prompt = build_prompt(pdf_text, article)
            raw = extractor.extract(prompt)

            start = raw.find("{")
            end = raw.rfind("}") + 1
            stored = json.loads(raw[start:end])

            print(f"✅ Forced Success: {stored.get('title')}")

        except Exception as e:
            print(f"❌ Forced extraction failed: {e}")

    # 🔥 SMART FALLBACK (last resort)
    if not stored:
        print("🔥 Using smart fallback")

        fallback_item = news_list[0]

        selected_url = fallback_item.get("link", "")
        selected_date = fallback_item.get("date")

        stored = {
            "title": fallback_item.get("title", "AI News Update"),
            "summary": fallback_text[:300] if fallback_text else "Latest AI update",
            "category": "AI",
            "key_tech": "AI",
            "impact": "Latest developments in AI"
        }

    # 🔹 Final payload
    final_payload = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Published Date": format_date(selected_date),
        "Title": stored.get("title"),
        "Link": selected_url,
        "HeadLine": stored.get("title"),
        "Summary": stored.get("summary"),
        "category": stored.get("category"),
        "key tech": stored.get("key_tech"),
        "impact": stored.get("impact"),
    }

    send(final_payload)
    save(list(visited))

    print("📊 Stored successfully")


if __name__ == "__main__":
    run()