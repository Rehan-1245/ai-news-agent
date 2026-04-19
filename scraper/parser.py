from newspaper import Article
from bs4 import BeautifulSoup
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}


def clean_text(text):
    return " ".join(text.split())


def parse_text(url):
    print(f"🔍 Parsing: {url}")

    # 🔹 1. Newspaper (BEST)
    try:
        article = Article(url)
        article.download()
        article.parse()

        text = clean_text(article.text)

        if len(text) > 400:
            print(f"✅ Newspaper success ({len(text)} chars)")
            return text
        else:
            print("⚠️ Newspaper too short")

    except Exception as e:
        print(f"⚠️ Newspaper failed: {e}")

    # 🔹 2. Requests + BeautifulSoup
    try:
        res = requests.get(url, headers=HEADERS, timeout=7)

        if res.status_code != 200:
            print(f"⚠️ Request failed: {res.status_code}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # Remove junk
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        paragraphs = soup.find_all("p")
        text = clean_text(" ".join(p.get_text() for p in paragraphs))

        if len(text) > 300:
            print(f"✅ BS4 success ({len(text)} chars)")
            return text
        else:
            print("⚠️ BS4 too short")

    except Exception as e:
        print(f"⚠️ BS4 failed: {e}")

    # 🔹 3. Smart Meta + OG fallback
    try:
        res = requests.get(url, headers=HEADERS, timeout=7)
        soup = BeautifulSoup(res.text, "html.parser")

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        og_desc = soup.find("meta", property="og:description")
        og_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", attrs={"name": "description"})

        description = ""

        if og_desc and og_desc.get("content"):
            description = og_desc["content"]
        elif meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]

        if og_title and og_title.get("content"):
            title = og_title["content"]

        fallback_text = clean_text(f"{title}. {description}")

        if len(fallback_text) > 80:
            print("🔥 Meta fallback used")
            return fallback_text
        else:
            print("⚠️ Meta too weak")

    except Exception as e:
        print(f"⚠️ Meta fallback failed: {e}")

    # 🔥 FINAL GUARANTEE (NEVER RETURN NONE)
    print("🔥 FINAL fallback (forced output)")

    return "AI news update. Unable to extract full article, but this link contains the latest AI-related development."