from django.db import models

from roze.models.abstract import Timestampable


class Location(Timestampable):
    name: models.TextField = models.TextField(
        blank=False,
        null=False,
    )
    light_in_lux: models.IntegerField = models.IntegerField(
        blank=True,
        null=True,
    )
    room: models.ForeignKey = models.ForeignKey(
        "Room",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.room.name}"
