"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.views.generic import TemplateView

from roze.views import (
    index,
    add_flower,
    edit_flower,
    view_flower,
    add_representational_photo,
    add_room,
    edit_room,
    add_location,
    edit_location,
    log_event,
    rooms_and_locations,
    water_flower,
    fertilise_flower,
    repot_flower,
    snooze_watering,
    archive_flower,
    register_webpush_device,
)

urlpatterns = [
    path("", index),
    path("roza/<int:flower_id>/", view_flower),
    path("roza/<int:flower_id>/edit/", edit_flower),
    path("roza/<int:flower_id>/add_photo/", add_representational_photo),
    path("roza/<int:flower_id>/log_event/", log_event),
    path("roza/<int:flower_id>/water/", water_flower),
    path("roza/<int:flower_id>/fertilise/", fertilise_flower),
    path("roza/<int:flower_id>/repot/", repot_flower),
    path("roza/<int:flower_id>/archive/", archive_flower),
    path("roza/<int:flower_id>/snooze_watering/<int:midnights>/", snooze_watering),
    path("add_flower/", add_flower),
    path("add_room/", add_room),
    path("room/<int:room_id>/edit/", edit_room),
    path("add_location/", add_location),
    path("location/<int:location_id>/edit/", edit_location),
    path("rooms_and_locations/", rooms_and_locations),
    path("register_webpush_device/", register_webpush_device),
    # WebPush service worker needs to be served from root to have full scope.
    path(
        "webPush.service.js",
        TemplateView.as_view(
            template_name="webPush.service.js", content_type="application/x-javascript"
        ),
    ),
]
