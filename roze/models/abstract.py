from django.db import models


class Timestampable(models.Model):
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
    )
    last_modified_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True
