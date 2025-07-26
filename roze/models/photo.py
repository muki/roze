from django.db import models

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose

from roze.models.abstract import Timestampable


class Photo(Timestampable):
    image: models.ImageField = models.ImageField(
        blank=False,
        null=False,
    )


class RepresentationalPhoto(Photo):
    flower: models.ForeignKey = models.ForeignKey(
        "Flower",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    thumbnail = ImageSpecField(
        source="image",
        processors=[Transpose(), ResizeToFill(112, 112)],
        format="JPEG",
        options={"quality": 90},
    )

    def __str__(self):
        if self.flower:
            return f"Photo of {self.flower.name}"
        else:
            return f"Photo of unknown flower"
