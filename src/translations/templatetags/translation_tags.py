from datetime import timedelta

from django import template
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import gettext

register = template.Library()


@register.simple_tag
def localized_datetime(value, action):
    if not value:
        return ""

    value = timezone.localtime(value)
    today = timezone.localdate()
    date = value.date()
    time = value.strftime("%H:%M")

    if date == today:
        date_label = gettext("today")
    elif date == today - timedelta(days=1):
        date_label = gettext("yesterday")
    else:
        date_label = date_format(
            date,
            format="DATE_FORMAT",
            use_l10n=True,
        )

    if action == "published":
        if date in (today, today - timedelta(days=1)):
            return gettext("Published %(date)s at %(time)s") % {
                "date": date_label,
                "time": time,
            }

        return gettext("Published on %(date)s at %(time)s") % {
            "date": date_label,
            "time": time,
        }

    if action == "modified":
        if date in (today, today - timedelta(days=1)):
            return gettext("modified %(date)s at %(time)s") % {
                "date": date_label,
                "time": time,
            }

        return gettext("modified on %(date)s at %(time)s") % {
            "date": date_label,
            "time": time,
        }

    return f"{date_label} {time}"
