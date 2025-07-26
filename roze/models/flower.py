from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from roze.models.abstract import Timestampable
from roze.models.managers import NonArchivedFlowersManager
from roze.models.event import Event
from roze.models.snooze import Snooze
from roze.time_math import just_after_midnight, midnights_between


class NoEvents(Exception):
    pass


class Flower(Timestampable):
    # Flower messages
    class MESSAGES:
        WATERING_SUCCESS = "🪧 Watering logged successfully. 💧"
        FERTILISATION_SUCCESS = "🪧 Fertilisation logged successfully. 💩"
        REPOTTING_SUCCESS = "🪧 Repotting logged successfully. 🪴"

    name: models.TextField = models.TextField(
        blank=False,
        null=False,
    )
    scientific_name: models.TextField = models.TextField(
        blank=True,
        null=True,
    )
    location: models.ForeignKey = models.ForeignKey(
        "Location", null=True, blank=True, on_delete=models.SET_NULL
    )
    watering_interval: models.IntegerField = models.IntegerField(
        blank=True,
        null=True,
        default=None,
    )
    fertilisation_interval: models.IntegerField = models.IntegerField(
        blank=True,
        null=True,
        default=None,
    )
    archived: models.BooleanField = models.BooleanField(
        blank=False,
        null=False,
        default=False,
    )
    # managers
    # first, the default one
    objects = models.Manager()
    # non archived flowers manager manager
    non_archived_flowers = NonArchivedFlowersManager()

    def __str__(self) -> str:
        return self.name

    def representational_photo_url(self):
        return self.representationalphoto_set.all().latest("last_modified_at").image.url

    def representational_photo_thumbnail_url(self):
        print(self.representationalphoto_set.all().latest("last_modified_at").thumbnail)
        return (
            self.representationalphoto_set.all()
            .latest("last_modified_at")
            .thumbnail.url
        )

    # action functions
    def midnights_since_last_action(
        self,
        event_type: str,
        current_time: datetime,
    ) -> int:
        """
        Counts midnights since last action.
        WARNING! Does not include snoozes.
        """

        latest_event = self.latest_event_of_type(event_type=event_type)

        # we have current_time, we have latest_event, time to return
        return midnights_between(current_time, latest_event.timestamp)

    def midnights_to_next_action(
        self,
        action_interval: int,
        event_type: str,
        current_time: datetime,
    ) -> int:
        """
        Counts midnights to next action.
        Can be negative.
        WARNING! Includes snoozes.
        """

        current_time = timezone.now()

        latest_event = self.latest_event_of_type(event_type=event_type)
        later_snoozes = Snooze.objects.filter(
            flower=self, event_type=event_type, created_at__gte=latest_event.timestamp
        )

        # no snoozes, count from event
        if later_snoozes.count() == 0:
            return midnights_between(
                current_time,
                (latest_event.timestamp + timedelta(days=(action_interval))),
            )

        # just one snooze, count from there
        if later_snoozes.count() == 1:
            return midnights_between(
                current_time,
                (
                    later_snoozes.first().created_at  # type: ignore
                    + timedelta(days=later_snoozes.first().midnights)  # type: ignore
                ),
            )

        # multiple snoozes, count from latest
        if later_snoozes.count() > 1:
            latest_snooze = later_snoozes[0]

            for current_snooze in later_snoozes[1:]:
                if (
                    current_snooze.created_at + timedelta(days=current_snooze.midnights)
                ) > (
                    latest_snooze.created_at + timedelta(days=latest_snooze.midnights)
                ):
                    latest_snooze = current_snooze

            return midnights_between(
                current_time,
                (latest_snooze.created_at + timedelta(days=latest_snooze.midnights)),
            )

        raise Exception("Something went terribly wrong here.")

    def needs_action_of_type(
        self,
        action_interval: int,
        event_type: str,
        current_time: datetime,
    ) -> bool:
        # if self.midnights_to_next_action returns NoEvents return False, otherwise do the math
        try:
            midnights_to_next_action = self.midnights_to_next_action(
                action_interval, event_type, current_time
            )

            return midnights_to_next_action < 1

        except NoEvents:
            return False

    def latest_event_of_type(self, event_type: str) -> Event:
        latest_event_or_none = (
            Event.objects.filter(flower=self, event_type=event_type)
            .order_by("-timestamp")
            .first()
        )

        # if no event of this type was found, raise a NoEvents
        if latest_event_or_none is None:
            raise NoEvents(
                f"No events of type {event_type} found for this flower (pk {self.pk})."
            )

        return latest_event_or_none

    def running_event_type_interval_average(
        self,
        event_type: str,
        current_time: datetime,
        number_of_days_included: int,
    ) -> float:
        action_timestamp_limit = just_after_midnight(
            current_time - timedelta(days=number_of_days_included)
        )

        event_timestamps = (
            Event.objects.filter(
                flower=self,
                event_type=event_type,
                timestamp__gte=action_timestamp_limit,
            )
            .order_by("-timestamp")
            .values_list("timestamp", flat=True)
        )
        event_timestamp_pairs = zip(event_timestamps, event_timestamps[1:])
        event_intervals_in_days = [
            (event_timestamp_pair[0] - event_timestamp_pair[1]).days
            for event_timestamp_pair in event_timestamp_pairs
        ]

        if len(event_intervals_in_days) == 0:
            return 0

        return sum(event_intervals_in_days) / len(event_intervals_in_days)

    # watering functions
    def needs_watering(self, current_time: datetime) -> bool:
        # if a watering_interval is set, investigate further
        if self.watering_interval is not None:
            return self.needs_action_of_type(
                self.watering_interval, Event.WATERING, current_time
            )
        # if the flower does not have a watering_interval set
        # the flower does not need to be watered
        else:
            return False

    @property
    def needs_watering_today(self) -> bool:
        return self.needs_watering(timezone.now())

    @property
    def latest_watering(self):
        return self.latest_event_of_type(Event.WATERING)

    @property
    def midnights_since_last_watering(self) -> int:
        current_time = timezone.now()
        # first we find the time today, one minute after midnight
        return self.midnights_since_last_action(
            event_type=Event.WATERING, current_time=current_time
        )

    @property
    def midnights_to_next_watering(self) -> int:
        # if watering_interval is not set, raise NotImplementedError
        if self.watering_interval is None:
            raise NotImplementedError(
                f"No watering interval set for flower with pk {self.pk}."
            )

        current_time = timezone.now()
        return self.midnights_to_next_action(
            action_interval=self.watering_interval,
            event_type=Event.WATERING,
            current_time=current_time,
        )

    @property
    def ninety_day_running_average_watering_interval(self) -> int:
        return round(
            self.running_event_type_interval_average(Event.WATERING, timezone.now(), 90)
        )

    # TODO This should probably use a proper library for time humanisation
    @property
    def midnights_to_next_watering_text(self) -> str:
        # maybe watering_interval is not set
        # but try the happy path first
        try:
            if self.midnights_to_next_watering < 1:
                return "Scheduled for today."
            elif self.midnights_to_next_watering == 1:
                return "Scheduled for tomorrow."
            else:
                return f"Scheduled in {self.midnights_to_next_watering} days."

        # no watering events so far
        except NoEvents:
            return f"No events logged."

        # watering_interval actually not set
        except NotImplementedError:
            return f"This plant should not be watered."

    @property
    def watering_urgency_sort_key(self) -> int:
        # maybe watering_interval is not set
        # but try the happy path first
        try:
            return self.midnights_to_next_watering
        except NoEvents:
            return 0
        # if the watering interval is not set
        # sort at the end of the list
        except NotImplementedError:
            return 999

    # fertilisation actions
    def needs_fertilisation(self, current_time: datetime) -> bool:
        # if a fertilisation_interval is set, investigate further
        if self.fertilisation_interval is not None:
            return self.needs_action_of_type(
                self.fertilisation_interval, Event.FERTILISATION, current_time
            )
        # if the flower does not have a fertilisation_interval set
        # the flower does not need to be fertilised
        else:
            return False

    @property
    def needs_fertilisation_today(self) -> bool:
        return self.needs_fertilisation(timezone.now())

    @property
    def latest_fertilisation(self):
        return self.latest_event_of_type(Event.FERTILISATION)

    @property
    def midnights_since_last_fertilisation(self) -> int:
        current_time = timezone.now()
        # first we find the time today, one minute after midnight
        return self.midnights_since_last_action(
            event_type=Event.FERTILISATION, current_time=current_time
        )

    @property
    def midnights_to_next_fertilisation(self) -> int:
        # if fertilisation_interval is not set, raise NotImplementedError
        if self.fertilisation_interval is None:
            raise NotImplementedError(
                f"No fertilisation interval set for flower with pk {self.pk}."
            )

        current_time = timezone.now()
        return self.midnights_to_next_action(
            action_interval=self.fertilisation_interval,
            event_type=Event.FERTILISATION,
            current_time=current_time,
        )

    # TODO This should probably use a proper library for time humanisation
    @property
    def midnights_to_next_fertilisation_text(self) -> str:
        # maybe fertilisation_interval is not set
        # but try the happy path first
        try:
            if self.midnights_to_next_fertilisation < 1:
                return "Fertilisation scheduled for today."
            if self.midnights_to_next_fertilisation == 1:
                return "Fertilisation scheduled for tomorrow."
            else:
                return f"Fertilisation scheduled in {self.midnights_to_next_fertilisation} days."

        # no fertilisation events so far
        except NoEvents:
            return f"No fertilisation events logged for this plant."

        # fertilisation_interval actually not set
        except NotImplementedError:
            return f"This plant should not be fertilised."

    @property
    def fertilisation_urgency_sort_key(self) -> int:
        # maybe fertilisation_interval is not set
        # but try the happy path first
        try:
            return self.midnights_to_next_fertilisation
        except NoEvents:
            return 0
        # if the fertilisation interval is not set
        # sort at the end of the list
        except NotImplementedError:
            return 999

    # repotting functions
    @property
    def latest_repotting(self) -> Event | None:
        try:
            return self.latest_event_of_type(Event.REPOTTING)
        except NoEvents:
            return None
