from django import forms

from roze.models import Event, Flower, RepresentationalPhoto, Room, Location


# class TextInputForm(forms.Widget):
#     def render(self, name, value, attrs=None):
#         return mark_safe('<input type="text" value="%s">' % value)


class FlowerForm(forms.ModelForm):
    name = forms.CharField()
    scientific_name = forms.CharField(
        required=False,
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by("room__name", "name"),
        to_field_name="id",
        empty_label="Select location",
    )
    representational_photo = forms.ImageField(required=False)
    watering_interval = forms.IntegerField(
        required=False,
        label_suffix=" (in days):",
        min_value=0,
    )
    fertilisation_interval = forms.IntegerField(
        required=False,
        label_suffix=" (in days):",
        min_value=0,
    )

    class Meta:
        model = Flower
        fields = (
            "name",
            "scientific_name",
            "location",
            "watering_interval",
            "fertilisation_interval",
            "representational_photo",
        )


class RepresentationalPhotoForm(forms.ModelForm):
    # image = forms.ImageField()
    # flower = forms.ModelChoiceField(
    #     queryset=Flower.non_archived_flowers.all(), to_field_name="id", empty_label="Select flower"
    # )

    class Meta:
        model = RepresentationalPhoto
        fields = (
            "image",
            "flower",
        )


class RoomForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Room
        fields = ("name",)


class LocationForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Location
        fields = (
            "name",
            "light_in_lux",
            "room",
        )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "note",
            "flower",
            "event_type",
            "timestamp",
        )
