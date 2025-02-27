from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db import connection
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time
from django.utils.timezone import now
from forwarder.models import Message


@shared_task
def process_messages():
    """Background process to update QUEUED messages to SENT."""
    while True:
        # Prevents database connection issues in multiprocessing
        with connection.cursor():
            messages = Message.objects.filter(status="QUEUED").order_by("created_at")
            for msg in messages:

                print(f"Message {msg.id} sent to {msg.recipient}")
                # send message via websocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "chat_group",
                    {
                        "type": "chat.message",
                        "message": f"{msg.recipient}|{msg.message}",
                    },
                )
                msg.status = "SENT"
                msg.sent_at = now()
                msg.save()

                time.sleep(1)  # Avoids high CPU usage, runs every 5 seconds

        time.sleep(5)


# --------------- for clearing queue ----------------
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=5,
    period=IntervalSchedule.SECONDS,
)

# Schedule the periodic task programmatically
periodic_task_instance, created = PeriodicTask.objects.get_or_create(
    name="Dispatch SMS",
    defaults={
        "task": "forwarder.tasks.process_messages",
        "interval": schedule,
    },
)

# If the task already exists, you may want to update it
if not created:
    periodic_task_instance.interval = schedule
    periodic_task_instance.task = "forwarder.tasks.process_messages"
    periodic_task_instance.save()
