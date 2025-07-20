import smtplib
from fastapi import HTTPException
import feedparser
from .celery_worker import celery_app
import aiosmtplib
from email.message import EmailMessage
import os
from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
load_dotenv()
translate_client = translate.Client()


@celery_app.task
def send_email_background(to_email: str, subject: str, body: str):
    print("📨 Starting email task...")

    try:
        SMTP_USER = os.getenv("SMTP_USER")
        SMTP_PASS = os.getenv("SMTP_PASS")
        print("SMTP_USER:", os.getenv("SMTP_USER"))  # check correct
        print("SMTP_PASS:", os.getenv("SMTP_PASS"))  # never print in production


        if not SMTP_USER or not SMTP_PASS:
            print("Missing SMTP credentials!")
            return

        message = EmailMessage()
        message["From"] = SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        print(f"Sending email to {to_email}...")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(message)

        print("✅ Email sent successfully.")

    except Exception as e:
        print(f"Failed to send email: {e}")


RSS_FEEDS = {
    "AI": "https://rss.feedspot.com/ai_rss_feeds/feed.xml",                 # Top AI feeds including Machine Learning Mastery, MIT, Google :contentReference[oaicite:1]{index=1}
    "SPACE": "https://www.space.com/feeds/news",                           # Space.com official feed :contentReference[oaicite:2]{index=2}
    "WORLD": "http://feeds.bbci.co.uk/news/world/rss.xml",                 # BBC World News (kept as is – widely reliable)
    "POLITICS": "https://www.politico.com/rss/politics08.xml",             # Politico Politics RSS :contentReference[oaicite:3]{index=3}
    "BUSINESS": "https://www.wsj.com/xml/rss/3_7014.xml",                   # WSJ Business (kept – works)
    "TECHNOLOGY": "https://www.wired.com/feed/category/gear/latest/rss",   # WIRED Gear or top stories :contentReference[oaicite:4]{index=4}
    "SCIENCE": "https://www.sciencedaily.com/rss/top/science.xml",         # ScienceDaily (kept – works)
    "ENTERTAINMENT": "http://feeds.ew.com/ew/latest",                      # Entertainment Weekly latest RSS
    "SPORTS": "https://www.espn.com/espn/rss/news",                        # ESPN News (kept – works)
    "HEALTH": "https://www.medicalnewstoday.com/rss",                      # MedicalNewsToday (kept – works)
    "ENVIRONMENT": "https://www.npr.org/rss/rss.php?id=1039",              # NPR Environment (kept – works)
    "AUTOMOTIVE": "https://feeds.autoblog.com/weblogsinc/autoblog.xml"     # Autoblog automotive feed
}


@celery_app.task
def fetch_articles(topics: list[str]) -> list[dict]:
    try:
        
        articles = []
        for topic in topics:
            if topic in RSS_FEEDS:
                feed_url = RSS_FEEDS[topic]
                feed = feedparser.parse(feed_url)

                if feed.bozo:
                    print(f"Error parsing feed for topic '{topic}': {feed.bozo_exception}")
                    continue

                print(f"Fetched {len(feed.entries)} entries for topic: {topic}")
                for entry in feed.entries:
                    summary = entry.get("summary", "").replace("&#8230;", "...").split("The post")[0]
                    articles.append({
                        "title": entry.get("title", "No Title"),
                        "link": entry.get("link", "#"),
                        "summary": summary,
                        "published": entry.get("published", "N/A"),
                        "author": entry.get("author", "Unknown")
                    })
            else:
                print("error")
        print(articles)
        return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch articles")




