from typing import List, Tuple

import json

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

import requests

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User  # TODO maybe inherit this in roze.models

from push_notifications.models import WebPushDevice

from roze.models import Flower


def send_notification(title: str, message: str, url: str) -> str:
    for app_token in settings.GOTIFY_APP_TOKENS.values():
        requests.post(
            f"{settings.GOTIFY_URL_BASE}/message?token={app_token}",
            json={
                "title": title,
                "message": message,
                "extras": {
                    "client::notification": {
                        "click": {
                            "url": f"{url}",
                        },
                    },
                },
            },
        )

    return f"Sent the following:\n\n{title}\n{message}"


def send_signal_notification(
    message: str,
    recipients: List[str],
) -> str:
    requests.post(
        f"{settings.SIGNAL_API_URL_BASE}/v2/send",
        json={
            "message": message,
            "number": settings.SIGNAL_NUMBER,
            "recipients": recipients,
        },
        headers={"content-type": "application/json"},
    )

    return f"Sent the following to {recipients}:\n\n{message}"


def send_webpush_notification(
    title: str,
    message: str,
    recipient: User,
) -> str:
    for device in recipient.webpushdevice_set.all():
        data = json.dumps({"title": title, "message": message})

        device.send_message(data)

    return f"Sent the following to {recipient}:\n\n{title}\n{message}"


# @db_periodic_task(settings.NOTIFICATION_INTERVAL)
def send_watering_notifications():
    flowers_that_need_watering = [
        flower
        for flower in Flower.non_archived_flowers.all()
        if flower.needs_watering(timezone.now())
    ]

    for flower in flowers_that_need_watering:
        title = f"🪻 {flower.name} needs 💧"
        message = f"Time to water your {flower.name}."
        url = f"{settings.URL_BASE}/roza/{flower.id}/"
        notification_result = send_notification(title, message, url)

    return f"Sent {len(flowers_that_need_watering)} notifications. Here is the final one:\n{notification_result}"


def send_grouped_watering_notifications() -> str:
    flowers_that_need_watering = [
        flower
        for flower in Flower.non_archived_flowers.all()
        if flower.needs_watering(timezone.now())
    ]

    if len(flowers_that_need_watering) > 0:
        title = "🪻 Your flowers need 💧"
        message = "Today is the day to water some of your plants."
        url = f"{settings.URL_BASE}/"
        notification_result = send_notification(title, message, url)

        return f"Sent:\n{notification_result}"

    return "Nothing to send."


def send_grouped_fertilisation_notifications() -> str:
    flowers_that_need_fertilisation = [
        flower
        for flower in Flower.non_archived_flowers.all()
        if flower.needs_fertilisation(timezone.now())
    ]

    if len(flowers_that_need_fertilisation) > 0:
        title = "🪻 Your flowers need 💩"
        message = "Today is the day to fertilise some of your plants."
        url = f"{settings.URL_BASE}/"
        notification_result = send_notification(title, message, url)

        return f"Sent:\n{notification_result}"

    return "Nothing to send."


def craft_signal_notification() -> str:
    # initiate message
    message = ""

    flowers_that_need_watering = [
        flower
        for flower in Flower.non_archived_flowers.all()
        if flower.needs_watering(timezone.now())
    ]

    if len(flowers_that_need_watering) > 0:
        message += "🪻 Your flowers need 💧\n"
        message += f"Today is the day to water {len(flowers_that_need_watering)} of your plants.\n"
        message += f"{settings.URL_BASE}/"

    return message


def craft_webpush_notification() -> Tuple[str, str]:
    # initiate message
    message = ""

    flowers_that_need_watering = [
        flower
        for flower in Flower.non_archived_flowers.all()
        if flower.needs_watering(timezone.now())
    ]

    if len(flowers_that_need_watering) > 0:
        title = "🪻 Your flowers need 💧"
        message += f"Today is the day to water {len(flowers_that_need_watering)} of your plants."

    return (
        title,
        message,
    )


@db_periodic_task(settings.NOTIFICATION_INTERVAL)
def send_all_notifications() -> str:
    result_string = ""

    # send watering notifications
    result_string += send_grouped_watering_notifications()

    result_string += "\n"

    # send fertilisation notifications
    result_string += send_grouped_fertilisation_notifications()

    # send signal notification (currently only watering)
    if message := craft_signal_notification():
        send_signal_notification(message, settings.SIGNAL_RECIPIENTS)

        # send webpush notification (currently only watering)
        # currently also assumes single tennancy
        # and piggybacks on signal notifications
        title, message = craft_webpush_notification()
        for user in User.objects.all():
            send_webpush_notification(title, message, user)

    return result_string
