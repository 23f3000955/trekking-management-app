from celery import Celery
from celery.schedules import crontab


def make_celery(app):

    celery = Celery(app.import_name)

    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        timezone="Asia/Kolkata",
        beat_schedule={
            "daily-reminders": {
                "task": "tasks.send_daily_reminders",
                "schedule": crontab(hour=8, minute=0),
            },
            "monthly-report": {
                "task": "tasks.send_monthly_report",
                "schedule": crontab(day_of_month=1, hour=0, minute=5),
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery