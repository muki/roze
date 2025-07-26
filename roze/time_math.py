from typing import List

from datetime import datetime, timedelta

from django.utils.timezone import make_aware


def just_after_midnight(the_time: datetime) -> datetime:
    return datetime(
        the_time.year,
        the_time.month,
        the_time.day,
        0,
        0,
        1,
    )


def midnights_between(first_datetime: datetime, second_datetime: datetime) -> int:
    if first_datetime < second_datetime:
        sooner = first_datetime
        later = second_datetime
    else:
        sooner = second_datetime
        later = second_datetime

    # first we find the sooner day, one minute after midnight
    after_sooner_midnight = make_aware(just_after_midnight(sooner))
    # then find the time after midnight on the later day
    after_later_midnight = make_aware(just_after_midnight(later))

    # return the timedelta days difference, counting midnights
    return (after_later_midnight - after_sooner_midnight).days
