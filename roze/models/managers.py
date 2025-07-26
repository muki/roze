from django.db import models


class NonArchivedFlowersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)
