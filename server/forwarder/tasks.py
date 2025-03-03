from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.db import connection
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time
from forwarder.models import Message
import redis

# Connect to Redis
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

LOCK_KEY = "celery:process_messages:lock"  # Unique key for the lock


@shared_task(bind=True)
def process_messages(self):
    """Background process to update QUEUED messages to SENT."""

    # Try to acquire lock, expire after 30 seconds
    lock = redis_client.setnx(LOCK_KEY, "locked")
    redis_client.expire(LOCK_KEY, 30)  # Initial expiration

    if not lock:
        print("Another instance of process_messages is already running. Skipping...")
        return  # Exit if the lock already exists

    try:
        with connection.cursor():
            messages = Message.objects.filter(
                status="QUEUED", inappropiate_content=False
            ).order_by("created_at")
            for i, msg in enumerate(messages):
                print(f"Message {msg.id} sent to {msg.recipient}")

                # Send message via WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "chat_group",
                    {
                        "type": "chat.message",
                        "message": f"{msg.recipient}|{msg.id}|{msg.message}",
                    },
                )
                time.sleep(5)  # Avoid high CPU usage
                # Extend expiration to prevent lock timeout
                redis_client.expire(LOCK_KEY, 30)

    finally:
        # Ensure the lock is released when the task completes
        redis_client.delete(LOCK_KEY)


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
