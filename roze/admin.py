from django.contrib import admin

from roze.models import (
    Flower,
    Location,
    Room,
    Event,
    RepresentationalPhoto,
    Snooze,
)

# Register your models here.

admin.site.register(Flower)
admin.site.register(Location)
admin.site.register(Room)
admin.site.register(Event)
admin.site.register(RepresentationalPhoto)


@admin.register(Snooze)
class SnoozeAdmin(admin.ModelAdmin):
    list_display = ["flower", "event_type", "snoozed_until"]

    readonly_fields = ["created_at"]
    fields = ["flower", "event_type", "midnights", "created_at"]
