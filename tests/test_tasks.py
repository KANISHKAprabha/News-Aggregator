from unittest.mock import patch,MagicMock
from news_aggregator.tasks import fetch_articles


from unittest.mock import patch, MagicMock
from news_aggregator.tasks import send_email_background

@patch("news_aggregator.tasks.smtplib.SMTP_SSL")
@patch("news_aggregator.tasks.os.getenv")
def test_send_email_background(mock_getenv, mock_smtp):
    # Mock environment variables
    mock_getenv.side_effect = lambda key: {
        "SMTP_USER": "test@gmail.com",
        "SMTP_PASS": "password123"
    }[key]

    # Mock SMTP server methods
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    send_email_background("to@example.com", "Test Subject", "Test Body")

    mock_server.login.assert_called_once_with("test@gmail.com", "password123")
    mock_server.send_message.assert_called_once()



from unittest.mock import patch, MagicMock
from news_aggregator.tasks import fetch_articles

@patch("news_aggregator.tasks.feedparser.parse")
def test_fetch_articles_success(mock_parse):
    mock_parse.return_value = MagicMock(
        bozo=False,
        entries=[
            {
                "title": "Test Article",
                "link": "https://example.com",
                "summary": "A test summary",
                "published": "2025-01-01",
                "author": "John Doe"
            }
        ]
    )

    topics = ["AI"]
    articles = fetch_articles(topics)

    assert len(articles) == 1
    assert articles[0]["title"] == "Test Article"
    assert articles[0]["link"] == "https://example.com"

@patch("news_aggregator.tasks.feedparser.parse")
def test_fetch_articles_invalid_feed(mock_parse):
    mock_parse.return_value = MagicMock(bozo=True, bozo_exception=Exception("Bad feed"))
    articles = fetch_articles(["AI"])
    assert articles == []
