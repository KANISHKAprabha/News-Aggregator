import smtplib
from fastapi import HTTPException
import feedparser
from .celery_worker import celery_app
import aiosmtplib
from email.message import EmailMessage
import os


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
    "AI": "https://www.analyticsvidhya.com/blog/category/artificial-intelligence/feed/",
    "SPACE": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "WORLD": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "POLITICS": "https://feeds.npr.org/1014/rss.xml",
    "BUSINESS": "https://www.wsj.com/xml/rss/3_7014.xml",
    "TECHNOLOGY": "https://www.theverge.com/rss/index.xml",
    "SCIENCE": "https://www.sciencedaily.com/rss/top/science.xml",
    "ENTERTAINMENT": "https://www.npr.org/rss/rss.php?id=1045",
    "SPORTS": "https://www.espn.com/espn/rss/news",
    "HEALTH": "https://www.medicalnewstoday.com/rss",
    "ENVIRONMENT": "https://www.npr.org/rss/rss.php?id=1039",
    "AUTOMOTIVE": "https://feeds.techxplore.com/automotive",
}

@celery_app.task
def fetch_articles(topics: list[str]) -> list[dict]:
 try:
    articles = []
    for topic in topics:
        if topic in RSS_FEEDS:
            feed = feedparser.parse(RSS_FEEDS[topic])
            for entry in feed.entries:
                summary = entry.get("summary", "").replace("&#8230;", "...").split("The post")[0]
                articles.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", "#"),
                    "summary": summary,
                    "published": entry.get("published", "N/A"),
                    "author": entry.get("author", "Unknown")
                })
    return articles
 except Exception as e:
    print(f"Error fetching articles: {e}")
    raise HTTPException(status_code=500, detail="Failed to fetch articles")