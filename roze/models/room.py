from django.db import models

from roze.models.abstract import Timestampable


class Room(Timestampable):
    name: models.TextField = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.name
