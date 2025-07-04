from celery import Celery

celery_app = Celery(
    "worker",
    broker = "redis://localhost:6380/0",
    backend= "redis://localhost:6380/0"
)
celery_app.autodiscover_tasks(["news_aggregator.tasks"])
celery_app.conf.task_routes = {
    "news_aggregator.tasks.*": {"queue": "email"},
}