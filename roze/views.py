from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils import timezone

from roze.time_math import just_after_midnight

from roze.models import Event, Flower, RepresentationalPhoto, Room, Location, Snooze

from roze.forms import (
    FlowerForm,
    RepresentationalPhotoForm,
    ListingRepresentationalPhotoForm,
    RoomForm,
    LocationForm,
    EventForm,
)


# Create your views here.
@never_cache
@login_required(login_url="/admin/login/")
def index(request):
    context = {}

    flowers = list(Flower.non_archived_flowers.all())
    flowers.sort(
        key=lambda flower: (
            min(
                [
                    flower.watering_urgency_sort_key,
                    flower.fertilisation_urgency_sort_key,
                ]
            ),
            flower.watering_urgency_sort_key,
            flower.fertilisation_urgency_sort_key,
        )
    )
    for flower in flowers:
        form_to_show = ListingRepresentationalPhotoForm(initial={"flower": flower.id})
        form_to_show.flower_id = flower.id
        flower.form = form_to_show

    context["flowers"] = flowers

    return render(request, "roze/flower_listing.html", context)


@login_required(login_url="/admin/login/")
def add_flower(request):
    context = {}

    if request.method == "POST":
        form = FlowerForm(request.POST, request.FILES)

        if form.is_valid():
            flower_instance = Flower(
                name=form.cleaned_data["name"],
                scientific_name=form.cleaned_data["scientific_name"],
                location=form.cleaned_data["location"],
                watering_interval=form.cleaned_data["watering_interval"],
                fertilisation_interval=form.cleaned_data["fertilisation_interval"],
            )
            flower_instance.save()

            if form.cleaned_data["representational_photo"]:
                representational_photo_instance = RepresentationalPhoto(
                    image=form.cleaned_data["representational_photo"],
                    flower=flower_instance,
                )
                representational_photo_instance.save()

            return HttpResponseRedirect("/")
        else:
            print(form.errors)

    form_to_show = FlowerForm
    context["form"] = form_to_show
    return render(request, "roze/photo_form.html", {"form": form_to_show})


@login_required(login_url="/admin/login/")
def edit_flower(request, flower_id):
    context = {}

    flower_instance = Flower.objects.get(id=flower_id)

    if request.method == "POST":
        form = FlowerForm(request.POST, request.FILES)

        if form.is_valid():
            flower_instance.name = form.cleaned_data["name"]
            flower_instance.scientific_name = form.cleaned_data["scientific_name"]
            flower_instance.location_id = form.cleaned_data["location"]
            flower_instance.watering_interval = form.cleaned_data["watering_interval"]
            flower_instance.fertilisation_interval = form.cleaned_data[
                "fertilisation_interval"
            ]
            flower_instance.save()

            if form.cleaned_data["representational_photo"]:
                representational_photo_instance = RepresentationalPhoto(
                    image=form.cleaned_data["representational_photo"],
                    flower=flower_instance,
                )
                representational_photo_instance.save()

            return HttpResponseRedirect(f"/roza/{flower_id}/")

    form_to_show = FlowerForm(
        initial={
            "name": flower_instance.name,
            "scientific_name": flower_instance.scientific_name,
            "location": flower_instance.location,
            "watering_interval": flower_instance.watering_interval,
            "fertilisation_interval": flower_instance.fertilisation_interval,
        }
    )
    context["form"] = form_to_show
    return render(request, "roze/photo_form.html", {"form": form_to_show})


@login_required(login_url="/admin/login/")
def view_flower(request, flower_id):
    flower_instance = Flower.objects.get(id=flower_id)

    current_time = timezone.now()
    log_timestamp_limit = just_after_midnight(current_time - timedelta(days=90))

    event_log = list(
        Event.objects.filter(
            flower=flower_instance,
            event_type=Event.WATERING,
            timestamp__gte=log_timestamp_limit,
        ).order_by("timestamp")
    )

    snooze_log = list(
        Snooze.objects.filter(
            flower=flower_instance,
            event_type=Event.WATERING,
            created_at=log_timestamp_limit,
        ).order_by("created_at")
    )
    for snooze in snooze_log:
        snooze.event_type += " SNOOZED"

    full_log = event_log + snooze_log
    full_log.sort(
        key=lambda event_or_snooze: (
            event_or_snooze.timestamp
            if hasattr(event_or_snooze, "timestamp")
            else event_or_snooze.created_at
        ),
        reverse=True,
    )

    latest_watering = (
        Event.objects.filter(flower=flower_instance, event_type=Event.WATERING)
        .order_by("timestamp")
        .last()
    )

    context = {
        "flower_instance": flower_instance,
        "full_log": full_log,
        "latest_watering": latest_watering,
        "needs_watering": flower_instance.needs_watering(timezone.now()),
    }

    return render(request, "roze/view_flower.html", context)


@login_required(login_url="/admin/login/")
def water_flower(request, flower_id):
    flower_instance = Flower.objects.get(id=flower_id)

    event = Event(
        flower=flower_instance, timestamp=timezone.now(), event_type=Event.WATERING
    )
    event.save()

    messages.success(request, Flower.MESSAGES.WATERING_SUCCESS)

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)

    return HttpResponseRedirect(f"/roza/{flower_id}")


@login_required(login_url="/admin/login/")
def snooze_watering(request, flower_id, midnights):
    flower_instance = Flower.objects.get(id=flower_id)

    snooze = Snooze(
        flower=flower_instance, midnights=midnights, event_type=Event.WATERING
    )
    snooze.save()

    messages.success(request, Snooze.MESSAGES.SNOOZE_SUCCESS(Event.WATERING, midnights))

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return HttpResponseRedirect(referer)

    return HttpResponseRedirect(f"/roza/{flower_id}")


@login_required(login_url="/admin/login/")
def snooze_fertilisation(request, flower_id, midnights):
    flower_instance = Flower.objects.get(id=flower_id)

    snooze = Snooze(
        flower=flower_instance, midnights=midnights, event_type=Event.FERTILISATION
    )
    snooze.save()

    messages.success(
        request, Snooze.MESSAGES.SNOOZE_SUCCESS(Event.FERTILISATION, midnights)
    )

    return HttpResponseRedirect(f"/roza/{flower_id}")


@login_required(login_url="/admin/login/")
def fertilise_flower(request, flower_id):
    flower_instance = Flower.objects.get(id=flower_id)

    event = Event(
        flower=flower_instance, timestamp=timezone.now(), event_type=Event.FERTILISATION
    )
    event.save()

    messages.success(request, Flower.MESSAGES.FERTILISATION_SUCCESS)

    return HttpResponseRedirect(f"/roza/{flower_id}")


@login_required(login_url="/admin/login/")
def repot_flower(request, flower_id):
    flower_instance = Flower.objects.get(id=flower_id)

    event = Event(
        flower=flower_instance, timestamp=timezone.now(), event_type=Event.REPOTTING
    )
    event.save()

    messages.success(request, Flower.MESSAGES.REPOTTING_SUCCESS)

    return HttpResponseRedirect(f"/roza/{flower_id}")


@login_required(login_url="/admin/login/")
def archive_flower(request, flower_id):
    flower_instance = Flower.objects.get(id=flower_id)

    flower_instance.archived = True
    flower_instance.save()

    return HttpResponseRedirect("/")


@login_required(login_url="/admin/login/")
def add_representational_photo(request, flower_id):
    context = {}

    if request.method == "POST":
        form = RepresentationalPhotoForm(request.POST, request.FILES)

        if form.is_valid():
            representational_photo_instance = RepresentationalPhoto(
                image=form.cleaned_data["image"],
                flower=form.cleaned_data["flower"],
            )
            representational_photo_instance.save()

            referer = request.META.get("HTTP_REFERER", f"/roza/{flower_id}")
            if "add_photo" in referer:
                return HttpResponseRedirect(f"/roza/{flower_id}")
            else:
                return HttpResponseRedirect(referer)

        else:
            return HttpResponse(form.errors)  # TODO handle better

    form_to_show = RepresentationalPhotoForm(initial={"flower": flower_id})
    context["form"] = form_to_show
    return render(request, "roze/photo_form.html", context)


@login_required(login_url="/admin/login/")
def add_room(request):
    context = {}

    if request.method == "POST":
        form = RoomForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(f"/")

        else:
            return HttpResponse(form.errors)  # TODO handle better

    form_to_show = RoomForm()
    context["form"] = form_to_show
    return render(request, "roze/generic_form.html", context)


@login_required(login_url="/admin/login/")
def edit_room(request, room_id):
    context = {}

    room_instance = Room.objects.get(id=room_id)

    if request.method == "POST":
        form = RoomForm(request.POST)

        if form.is_valid():
            room_instance.name = form.cleaned_data["name"]
            room_instance.save()

            return HttpResponseRedirect(f"/rooms_and_locations/")

        else:
            return HttpResponse(form.errors)  # TODO handle better

    form_to_show = RoomForm(initial={"name": room_instance.name})

    context["form"] = form_to_show
    return render(request, "roze/generic_form.html", context)


@login_required(login_url="/admin/login/")
def edit_location(request, location_id):
    context = {}

    location_instance = Location.objects.get(id=location_id)

    if request.method == "POST":
        form = LocationForm(request.POST)

        if form.is_valid():
            location_instance.name = form.cleaned_data["name"]
            location_instance.save()

            return HttpResponseRedirect(f"/rooms_and_locations/")

        else:
            return HttpResponse(form.errors)  # TODO handle better

    form_to_show = LocationForm(
        initial={
            "name": location_instance.name,
            "light_in_lux": location_instance.light_in_lux,
            "room": location_instance.room,
        }
    )

    context["form"] = form_to_show
    return render(request, "roze/generic_form.html", context)


@login_required(login_url="/admin/login/")
def add_location(request):
    context = {}

    if request.method == "POST":
        form = LocationForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(f"/")

        else:
            return HttpResponse(form.errors)  # TODO handle better

    if room_id := request.GET.get("room_id", False):
        form_to_show = LocationForm(initial={"room": Room.objects.get(id=room_id)})

    else:
        form_to_show = LocationForm()

    context["form"] = form_to_show
    return render(request, "roze/generic_form.html", context)


@login_required(login_url="/admin/login/")
def rooms_and_locations(request):
    context = {}

    rooms = [
        {"room": room, "locations": room.location_set.all().order_by("name")}
        for room in Room.objects.all().order_by("name")
    ]

    context["rooms"] = rooms

    return render(request, "roze/rooms_and_locations.html", context)


@login_required(login_url="/admin/login/")
def log_event(request, flower_id):
    context = {}

    flower_instance = Flower.objects.get(id=flower_id)

    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(f"/roza/{flower_id}/")

    form_to_show = EventForm(
        initial={
            "flower": flower_instance,
            "timestamp": timezone.now(),
        }
    )
    context["form"] = form_to_show
    return render(request, "roze/generic_form.html", {"form": form_to_show})
