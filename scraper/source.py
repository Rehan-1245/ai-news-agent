import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import email.utils as eut

HEADERS = {"User-Agent": "Mozilla/5.0"}

# 🔹 Sources
BASE_SOURCES = [
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/"
]

EXPANDED_SOURCES = [
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.artificialintelligence-news.com/feed/",
    "https://blog.google/technology/ai/rss/",
    "https://openai.com/news/rss.xml",
    "https://www.marktechpost.com/feed/",  # ✅ FIXED COMMA
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.wired.com/feed/rss"
]

FALLBACK_SOURCES = [
    "https://hnrss.org/newest?q=AI",
    "https://www.reddit.com/r/artificial/.rss"
]

# 🔥 Strong filtering
STRONG_AI_KEYWORDS = [
    "llm", "gpt", "model", "openai", "anthropic",
    "gemini", "ai model", "deep learning"
]

WEAK_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning"
]

BLACKLIST = [
    "tourism", "travel", "stock", "earnings",
    "opinion", "marketing", "festival"
]


def fetch_rss(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)

        if res.status_code != 200:
            return None

        if not res.text.strip().startswith("<"):
            return None

        return ET.fromstring(res.content)

    except:
        return None


def parse_date(date_str):
    try:
        return datetime(*eut.parsedate(date_str)[:6])
    except:
        return None


def is_recent(date, hours):
    if not date:
        return False
    return (datetime.utcnow() - date) <= timedelta(hours=hours)


# 🔥 STRONG relevance filter
def is_relevant(title):
    t = title.lower()

    # ❌ remove junk
    if any(b in t for b in BLACKLIST):
        return False

    # ✅ strong AI signals required
    if any(k in t for k in STRONG_AI_KEYWORDS):
        return True

    # fallback (weak signal but still AI-ish)
    if any(k in t for k in WEAK_KEYWORDS):
        return True

    return False


def score_article(title, source, date):
    score = 0
    t = title.lower()

    # 🔥 strong signals
    if any(k in t for k in STRONG_AI_KEYWORDS):
        score += 5

    # launches / releases
    if any(x in t for x in ["launch", "release", "new", "update"]):
        score += 3

    # big players boost
    if any(x in t for x in ["openai", "google", "anthropic", "meta"]):
        score += 3

    # source weight
    if "techcrunch" in source:
        score += 3
    elif "venturebeat" in source:
        score += 2
    elif "arstechnica" in source:
        score += 2

    # 🔥 freshness boost
    if date:
        hours_old = (datetime.utcnow() - date).total_seconds() / 3600
        if hours_old < 6:
            score += 5
        elif hours_old < 12:
            score += 3
        elif hours_old < 24:
            score += 2

    return score


def extract_articles(root, source, hours):
    articles = []

    if root is None:
        return articles

    for item in root.findall(".//item"):
        title = item.find("title")
        link = item.find("link")
        pub = item.find("pubDate")

        if title is None or link is None:
            continue

        date = parse_date(pub.text if pub is not None else "")

        if not is_recent(date, hours):
            continue

        title_text = title.text.strip()

        if not is_relevant(title_text):
            continue

        articles.append({
            "title": title_text,
            "link": link.text.strip(),
            "date": date,
            "score": score_article(title_text, source, date)
        })

    return articles


def get_sources(stage):
    if stage == 1:
        return BASE_SOURCES
    elif stage == 2:
        return BASE_SOURCES + EXPANDED_SOURCES
    else:
        return BASE_SOURCES + EXPANDED_SOURCES + FALLBACK_SOURCES


def get_ai_news_urls(limit=5):

    TIME_WINDOWS = [24, 48, 72]

    for hours in TIME_WINDOWS:
        for stage in [1, 2, 3]:

            sources = get_sources(stage)
            all_articles = []

            print(f"\n⏳ {hours}h | Stage {stage}")

            for source in sources:
                root = fetch_rss(source)
                articles = extract_articles(root, source, hours)
                all_articles.extend(articles)

            if all_articles:
                all_articles.sort(
                    key=lambda x: (x["score"], x["date"]),
                    reverse=True
                )

                seen = set()
                final = []

                for a in all_articles:
                    if a["link"] not in seen:
                        seen.add(a["link"])
                        final.append(a)

                print(f"✅ Found {len(final)} articles")

                return final[:limit]

    print("🔥 fallback triggered")

    return [{
        "title": "AI News Update",
        "link": "https://techcrunch.com/category/artificial-intelligence/",
        "date": datetime.utcnow(),
        "score": 0
    }]