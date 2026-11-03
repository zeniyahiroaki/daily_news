#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daily News Collector
12のメディアサイトから最新ニュースを取得・整理し、当日の記事一覧JSONを生成します。
"""

import os
import re
import json
import time
import hashlib
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
import feedparser
from bs4 import BeautifulSoup

# 日本標準時 (JST)
JST = timezone(timedelta(hours=9))

# メディアの定義
SOURCES = [
    {
        "id": "k-tai",
        "name": "ケータイ Watch",
        "type": "rss",
        "url": "https://k-tai.watch.impress.co.jp/data/rss/1.0/ktw/feed.rdf",
        "genre": "mobile",
        "genre_name": "モバイル・通信",
        "default_thumb": "https://k-tai.watch.impress.co.jp/include/common/p01/images/logo/ktw.1200.png"
    },
    {
        "id": "car-watch",
        "name": "Car Watch",
        "type": "rss",
        "url": "https://car.watch.impress.co.jp/data/rss/1.0/car/feed.rdf",
        "genre": "car",
        "genre_name": "自動車・モビリティ",
        "default_thumb": "https://car.watch.impress.co.jp/include/common/p01/images/logo/car.1200.png"
    },
    {
        "id": "ai-watch",
        "name": "AI Watch",
        "type": "rss",
        "url": "https://ai.watch.impress.co.jp/data/rss/1.0/aiw/feed.rdf",
        "genre": "tech",
        "genre_name": "テクノロジー・AI",
        "default_thumb": "https://ai.watch.impress.co.jp/include/common/p01/images/logo/aiw.1200.png"
    },
    {
        "id": "pc-watch",
        "name": "PC Watch",
        "type": "rss",
        "url": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf",
        "genre": "tech",
        "genre_name": "テクノロジー・AI",
        "default_thumb": "https://pc.watch.impress.co.jp/include/common/p01/images/logo/pcw.1200.png"
    },
    {
        "id": "dc-watch",
        "name": "デジカメ Watch",
        "type": "rss",
        "url": "https://dc.watch.impress.co.jp/data/rss/1.0/dcw/feed.rdf",
        "genre": "camera",
        "genre_name": "カメラ・写真",
        "default_thumb": "https://dc.watch.impress.co.jp/include/common/p01/images/logo/dcw.1200.png"
    },
    {
        "id": "kaden-watch",
        "name": "家電 Watch",
        "type": "rss",
        "url": "https://kaden.watch.impress.co.jp/data/rss/1.0/kdw/feed.rdf",
        "genre": "appliance",
        "genre_name": "家電・ライフ",
        "default_thumb": "https://kaden.watch.impress.co.jp/include/common/p01/images/logo/kdw.1200.png"
    },
    {
        "id": "itmedia-top",
        "name": "ITmedia Top",
        "type": "rss",
        "url": "https://rss.itmedia.co.jp/rss/2.0/topstory.xml",
        "genre": "tech",
        "genre_name": "テクノロジー・AI",
        "default_thumb": "https://image.itmedia.co.jp/images/logo/1200x630_500x500_top.gif"
    },
    {
        "id": "itmedia-mobile",
        "name": "ITmedia Mobile",
        "type": "rss",
        "url": "https://rss.itmedia.co.jp/rss/2.0/mobile.xml",
        "genre": "mobile",
        "genre_name": "モバイル・通信",
        "default_thumb": "https://image.itmedia.co.jp/mobile/images/logo/mobile_ogp.gif"
    },
    {
        "id": "gizmodo",
        "name": "ギズモード・ジャパン",
        "type": "rss",
        "url": "https://www.gizmodo.jp/feed/index.xml",
        "genre": "tech",
        "genre_name": "テクノロジー・AI",
        "default_thumb": "https://assets.media-cache.com/assets/gizmodo/img/common/logo-og.png"
    },
    {
        "id": "digicame-info",
        "name": "デジカメinfo",
        "type": "rss",
        "url": "https://digicame-info.com/atom.xml",
        "genre": "camera",
        "genre_name": "カメラ・写真",
        "default_thumb": "https://digicame-info.com/favicon.ico"
    },
    {
        "id": "dtm-station",
        "name": "DTMステーション",
        "type": "rss",
        "url": "https://www.dtmstation.com/feed",
        "genre": "music",
        "genre_name": "音楽・DJ",
        "default_thumb": "https://www.dtmstation.com/wp-content/uploads/2018/09/ogp.jpg"
    },
    {
        "id": "realsound-dj",
        "name": "Real Sound (DJ)",
        "type": "html",
        "url": "https://realsound.jp/tag/dj",
        "genre": "music",
        "genre_name": "音楽・DJ",
        "default_thumb": "https://realsound.jp/wp-content/themes/realsound/images/ogp.png"
    }
]

GENRE_ORDER = [
    {"id": "all", "name": "すべて"},
    {"id": "tech", "name": "テクノロジー・AI"},
    {"id": "mobile", "name": "モバイル・通信"},
    {"id": "camera", "name": "カメラ・写真"},
    {"id": "music", "name": "音楽・DJ"},
    {"id": "car", "name": "自動車・モビリティ"},
    {"id": "appliance", "name": "家電・ライフ"}
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def clean_html_text(raw_html):
    """HTMLタグを除去して純粋なテキストを抽出"""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    # 不要なスクリプトやスタイルを除去
    for element in soup(["script", "style", "noscript"]):
        element.extract()
    text = soup.get_text(separator=" ", strip=True)
    # 連続空白や改行を整理
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_date(date_str, parsed_struct=None):
    """公開日時をJST datetimeに変換"""
    if parsed_struct:
        try:
            dt_utc = datetime(*parsed_struct[:6], tzinfo=timezone.utc)
            return dt_utc.astimezone(JST)
        except Exception:
            pass

    if not date_str:
        return datetime.now(JST)

    # 一般的な日付文字列のパース
    patterns = [
        r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})",
        r"(\d{4})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2})",
        r"(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{4})/(\d{2})/(\d{2})"
    ]

    for pat in patterns:
        m = re.search(pat, date_str)
        if m:
            parts = [int(p) for p in m.groups()]
            try:
                if len(parts) >= 6:
                    return datetime(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], tzinfo=JST)
                elif len(parts) >= 5:
                    return datetime(parts[0], parts[1], parts[2], parts[3], parts[4], 0, tzinfo=JST)
                elif len(parts) >= 3:
                    return datetime(parts[0], parts[1], parts[2], 0, 0, 0, tzinfo=JST)
            except Exception:
                continue

    return datetime.now(JST)


def fetch_og_image(article_url, default_thumb=""):
    """記事URLのHTMLからog:imageサムネイルを取得"""
    if not article_url:
        return default_thumb
    try:
        resp = requests.get(article_url, headers=HEADERS, timeout=5, stream=True)
        # 先頭40KBだけ読み込んでOGPを探す
        chunk = resp.raw.read(40000, decode_content=True)
        encoding = resp.encoding or "utf-8"
        html_chunk = chunk.decode(encoding, errors="ignore")

        # og:imageを探す
        m = re.search(r'<meta[^>]+(?:property|name)=[\'"](?:og:image|twitter:image)[\'"][^>]+content=[\'"]([^\'"]+)[\'"]', html_chunk, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=[\'"]([^\'"]+)[\'"][^>]+(?:property|name)=[\'"](?:og:image|twitter:image)[\'"]', html_chunk, re.I)

        if m:
            img_url = m.group(1).strip()
            return urljoin(article_url, img_url)
    except Exception:
        pass
    return default_thumb


def fetch_rss_feed(source):
    """RSS/Atom/RDFフィードを取得して記事一覧をパース"""
    articles = []
    print(f"Fetching RSS: {source['name']} ({source['url']})")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=10)
        feed = feedparser.parse(resp.content)

        for entry in feed.entries[:25]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue

            # 公開日時の取得
            dt = parse_date(
                entry.get("published") or entry.get("updated") or entry.get("dc_date"),
                entry.get("published_parsed") or entry.get("updated_parsed")
            )

            # 概要テキストの取得
            raw_summary = entry.get("summary") or entry.get("description") or ""
            summary_text = clean_html_text(raw_summary)

            # サムネイル画像の探索
            thumbnail = ""
            # 1. enclosures
            if hasattr(entry, "enclosures") and entry.enclosures:
                for enc in entry.enclosures:
                    if enc.get("type", "").startswith("image"):
                        thumbnail = enc.get("href") or enc.get("url")
                        break
            # 2. media_content / media_thumbnail
            if not thumbnail and hasattr(entry, "media_content") and entry.media_content:
                for mc in entry.media_content:
                    if "image" in mc.get("type", "") or "url" in mc:
                        thumbnail = mc.get("url")
                        break
            if not thumbnail and hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                thumbnail = entry.media_thumbnail[0].get("url")
            # 3. HTML内のimgタグ
            if not thumbnail and raw_summary:
                img_m = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', raw_summary, re.I)
                if img_m:
                    thumbnail = img_m.group(1)

            # IDの生成（URLのハッシュ）
            art_id = hashlib.md5(link.encode("utf-8")).hexdigest()[:12]

            articles.append({
                "id": art_id,
                "title": title,
                "url": link,
                "media": source["name"],
                "source_id": source["id"],
                "genre": source["genre"],
                "genre_name": source["genre_name"],
                "thumbnail": thumbnail,
                "default_thumb": source["default_thumb"],
                "summary": summary_text,
                "published_dt": dt
            })
    except Exception as e:
        print(f"Error fetching RSS for {source['name']}: {e}")

    return articles


def fetch_realsound_dj(source):
    """Real Sound (DJタグ) ページをスクレイピング"""
    articles = []
    print(f"Scraping HTML: {source['name']} ({source['url']})")
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.content, "html.parser")

        entries = soup.select("article.entry-summary")
        for ent in entries[:20]:
            title_tag = ent.select_one("h2.entry-title a") or ent.select_one("h3.entry-title a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "").strip()
            if not link:
                continue
            link = urljoin(source["url"], link)

            # 日時
            time_tag = ent.select_one("time")
            date_str = ""
            if time_tag:
                date_str = time_tag.get("datetime") or time_tag.get_text(strip=True)
            dt = parse_date(date_str)

            # サムネイル
            thumbnail = ""
            fixed_ratio = ent.select_one(".fixed-ratio")
            if fixed_ratio and "background-image" in fixed_ratio.get("style", ""):
                m = re.search(r'url\((.*?)\)', fixed_ratio["style"])
                if m:
                    thumbnail = m.group(1).strip("'\"")
            if not thumbnail:
                img_tag = ent.select_one(".entry-thumb img")
                if img_tag:
                    thumbnail = img_tag.get("src") or img_tag.get("data-src")
            if thumbnail:
                thumbnail = urljoin(source["url"], thumbnail)

            # 概要
            excerpt_tag = ent.select_one(".entry-excerpt")
            summary_text = excerpt_tag.get_text(strip=True) if excerpt_tag else ""

            art_id = hashlib.md5(link.encode("utf-8")).hexdigest()[:12]

            articles.append({
                "id": art_id,
                "title": title,
                "url": link,
                "media": source["name"],
                "source_id": source["id"],
                "genre": source["genre"],
                "genre_name": source["genre_name"],
                "thumbnail": thumbnail,
                "default_thumb": source["default_thumb"],
                "summary": summary_text,
                "published_dt": dt
            })
    except Exception as e:
        print(f"Error scraping {source['name']}: {e}")

    return articles


def enrich_thumbnail(article):
    """サムネイルが空の場合にog:imageを取得"""
    if not article["thumbnail"]:
        article["thumbnail"] = fetch_og_image(article["url"], article["default_thumb"])
    return article


def generate_gemini_summary(title, summary, api_key):
    """Gemini APIで3行要約を生成"""
    if not api_key:
        return None

    prompt = f"""以下のニュース記事の情報を元に、日本語で要点を3つの簡潔な箇条書き（各行25〜45文字程度）でまとめてください。
出力はMarkdownの箇条書き（- で始まる行）のみを出力し、挨拶や前置きは含めないでください。

タイトル: {title}
記事内容抜粋: {summary}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 200
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                bullets = [re.sub(r"^[-*・\d.]\s*", "", line).strip() for line in text.strip().split("\n") if line.strip()]
                bullets = [b for b in bullets if b]
                if len(bullets) >= 2:
                    return bullets[:3]
    except Exception as e:
        print(f"Gemini API error: {e}")

    return None


def main():
    now_jst = datetime.now(JST)
    today_str = now_jst.strftime("%Y-%m-%d")
    yesterday_str = (now_jst - timedelta(days=1)).strftime("%Y-%m-%d")
    cutoff_time = now_jst - timedelta(hours=36) # 直近36時間以内の記事を対象に収集

    print(f"=== Starting Daily News Collection ({now_jst.strftime('%Y-%m-%d %H:%M:%S')} JST) ===")
    print(f"Today is: {today_str}")

    all_raw_articles = []

    # 1. 各ソースから収集
    for source in SOURCES:
        if source["type"] == "rss":
            items = fetch_rss_feed(source)
        else:
            items = fetch_realsound_dj(source)
        all_raw_articles.extend(items)

    print(f"Total raw articles collected: {len(all_raw_articles)}")

    # 2. 直近36時間以内の記事にフィルタリング（新しい順）
    recent_articles = [a for a in all_raw_articles if a["published_dt"] >= cutoff_time]
    # もし少なければ直近48時間に緩和
    if len(recent_articles) < 15:
        cutoff_time = now_jst - timedelta(hours=48)
        recent_articles = [a for a in all_raw_articles if a["published_dt"] >= cutoff_time]

    # 日時降順でソート
    recent_articles.sort(key=lambda x: x["published_dt"], reverse=True)

    # 重複URLの除外
    unique_articles = []
    seen_urls = set()
    for a in recent_articles:
        if a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            unique_articles.append(a)

    print(f"Articles after deduplication and time filter: {len(unique_articles)}")

    # 3. サムネイルの並列補完（og:image）
    print("Enriching thumbnails...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        unique_articles = list(executor.map(enrich_thumbnail, unique_articles))

    # 4. Gemini API による3行要約（環境変数 GEMINI_API_KEY がある場合）
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        print("GEMINI_API_KEY detected! Generating AI summaries for today's articles...")
        # 本日の記事（最大25件程度）を対象に要約
        summarized_count = 0
        for art in unique_articles:
            if art["published_dt"].strftime("%Y-%m-%d") == today_str and summarized_count < 25:
                bullets = generate_gemini_summary(art["title"], art["summary"], api_key)
                if bullets:
                    art["summary_bullets"] = bullets
                    art["summary"] = "\n".join([f"・{b}" for b in bullets])
                    summarized_count += 1
                    time.sleep(0.5)  # レートリミット配慮
        print(f"Generated AI summaries for {summarized_count} articles.")
    else:
        print("GEMINI_API_KEY not found or empty. Using default RSS summaries.")

    # 5. 出力用データの整形
    formatted_articles = []
    genre_counts = {g["id"]: 0 for g in GENRE_ORDER}
    today_count = 0

    for a in unique_articles:
        pub_dt = a["published_dt"]
        pub_date = pub_dt.strftime("%Y-%m-%d")
        pub_time = pub_dt.strftime("%H:%M")
        is_today = (pub_date == today_str)
        if is_today:
            today_count += 1

        genre_id = a["genre"]
        if genre_id in genre_counts:
            genre_counts[genre_id] += 1
        genre_counts["all"] += 1

        # 箇条書きがなければ、概要から簡易リストを作成
        summary_bullets = a.get("summary_bullets")
        if not summary_bullets:
            # 概要文を短く整える
            s_text = a["summary"]
            if len(s_text) > 180:
                s_text = s_text[:177] + "..."
            summary_bullets = [s_text] if s_text else ["（本文リンク先をご覧ください）"]

        formatted_articles.append({
            "id": a["id"],
            "title": a["title"],
            "url": a["url"],
            "media": a["media"],
            "genre": a["genre"],
            "genre_name": a["genre_name"],
            "thumbnail": a["thumbnail"] or a["default_thumb"],
            "summary": a["summary"] or a["title"],
            "summary_bullets": summary_bullets,
            "published_at": pub_dt.isoformat(),
            "published_date": pub_date,
            "published_time": pub_time,
            "is_today": is_today
        })

    # ジャンルリストにカウントを反映
    genres_with_counts = []
    for g in GENRE_ORDER:
        genres_with_counts.append({
            "id": g["id"],
            "name": g["name"],
            "count": genre_counts.get(g["id"], 0)
        })

    output_data = {
        "generated_at": now_jst.isoformat(),
        "generated_at_formatted": now_jst.strftime("%Y/%m/%d %H:%M"),
        "target_date": today_str,
        "yesterday_date": yesterday_str,
        "total_articles": len(formatted_articles),
        "today_articles_count": today_count,
        "genres": genres_with_counts,
        "articles": formatted_articles
    }

    # 出力先ディレクトリの確保
    output_dir = os.path.join(os.path.dirname(__file__), "..", "public", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "news.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved {len(formatted_articles)} articles ({today_count} today) to {output_path}")


if __name__ == "__main__":
    main()
