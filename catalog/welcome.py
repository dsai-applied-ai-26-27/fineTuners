"""What is put in front of a visitor unasked: the tour, once, and after that the news.

    first visit to the dashboard     the tour (templates/components/tour.html)
    any later visit                  "What's new", if something changed since they last saw
                                     it (templates/components/news.html)

Never both, and each at most once. What a person has seen is kept with their account
(accounts.Profile), not in the browser, so a second device or a cleared browser does not
bring the tour back. The tour is always the current one, so taking it also counts as
having seen every update so far.

Where nobody is signed in there is no account to remember anything; the browser does
(static/js/components/tour.js) and there is no news.
"""

from django.utils import timezone

from accounts.models import Profile

from . import news


def welcome(request):
    """What to offer this visitor on the page being built. Used by the pages people
    arrive at: the dashboard and a course's front page."""
    offer = {"tour": False, "news": []}
    if not request.user.is_authenticated:
        offer["tour"] = True
        return offer
    profile = Profile.objects.filter(user=request.user).first()
    if profile is None or profile.tour_seen_at is None:
        offer["tour"] = True
    else:
        offer["news"] = news.since(profile.news_seen)
    return offer


def mark_seen(user, what, upto):
    """Record that `user` was shown the tour or the news, up to update number `upto`.

    The number comes from the page that was shown, not from the list as it is now: a tab
    opened before a release has shown what was current then.
    """
    upto = max(0, min(upto, news.LATEST))
    # get_or_create: the row is made the first time there is something to record.
    profile, _ = Profile.objects.get_or_create(user=user)
    if what == "tour" and profile.tour_seen_at is None:
        profile.tour_seen_at = timezone.now()
        profile.tour_update = upto
    profile.news_seen = max(profile.news_seen, upto)
    profile.save()
    return profile


def toured_at(user):
    """The update that was current when this person took the tour, or None if they have
    not: everything numbered higher is new to them."""
    if not user.is_authenticated:
        return None
    profile = Profile.objects.filter(user=user, tour_seen_at__isnull=False).first()
    return profile.tour_update if profile else None
