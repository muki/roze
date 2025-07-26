from django.db import models
from django.utils import timezone

from roze.models.abstract import Timestampable

from roze.time_math import midnights_between


class Event(Timestampable):
    # Event types
    WATERING = "WATERING"
    FERTILISATION = "FERTILISATION"
    REPOTTING = "REPOTTING"
    # All together now
    EVENT_TYPES = (
        (
            WATERING,
            "watering",
        ),
        (
            FERTILISATION,
            "fertilisation",
        ),
        (
            REPOTTING,
            "repotting",
        ),
    )

    timestamp: models.DateTimeField = models.DateTimeField(blank=False, null=False)
    note: models.TextField = models.TextField(blank=True, null=True)
    flower: models.ForeignKey = models.ForeignKey("Flower", on_delete=models.CASCADE)
    event_type: models.CharField = models.CharField(
        max_length=100,
        choices=EVENT_TYPES,
        default=WATERING,
        blank=False,
        null=False,
    )

    def __str__(self):
        return f"{self.event_type}: {self.flower.name}"

    @property
    def midnights_since(self) -> int:
        current_time = timezone.now()
        return midnights_between(current_time, self.timestamp)
