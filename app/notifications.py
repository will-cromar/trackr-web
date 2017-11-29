"""Contains code to generate notifications for users."""
from datetime import date, timedelta
from app import db, models, cache
from .recommender import get_neighbors
import random
import time
import json


def batch_notifications():
    """Fills cache with JSON serialized notification dicts."""
    users = db.session.query(models.User).all()

    for user in users:
        recommendation = __fetch_recommendation(user)
        reminders = __fetch_schedule_data(user)
        notifications = recommendation + reminders
        for n in notifications:
            cache.lpush(user.username, json.dumps(n))


def notify_neighbors(listings, new_listing):
    """Notify the subscribers of neighboring listings of new content."""
    target_index = listings.index(new_listing)

    neighbors = get_neighbors(listings, target_index)
    notify_users = set()
    for n in neighbors:
        for s in n.subscribers:
            notify_users.add(s.username)

    for user in notify_users:
        notification = {
            'listing_id': new_listing.listing_id,
            'time': int(new_listing.release_date.timestamp()),
            'message': "New Content: {}".format(new_listing.title),
            'submessage': "Similar to content that you've subscribed to"
        }
        cache.lpush(user, json.dumps(notification))


def __fetch_recommendation(user):
    """Returns a list containing 0 or 1 recommendations for a user."""
    subs = user.subscriptions

    if len(subs) <= 0:
        return []

    # Pick a random subscription to recommend off of
    source = random.choice(subs)
    listings = models.Listing.query.all()
    target_index = listings.index(source)

    # Pick a random neighbor
    neighbors = get_neighbors(listings, target_index)
    if not neighbors:
        return []
    recommendation = random.choice(neighbors)

    return [{
        'listing_id': recommendation.listing_id,
        'time': int(recommendation.release_date.timestamp()),
        'message': "We recommend you try {}!".format(recommendation.title),
        'submessage': "Based on your interest in {}".format(source.title)
    }]


def __fetch_schedule_data(user):
    """Gathers a list of Schedule data per user and returns a dictionary
    of that data"""
    upcoming_schedule = db.session.query(
        models.Schedule.date, models.Schedule.listing_id,
        models.Listing.title) \
        .filter(models.Schedule.listing_id.in_([i.listing_id for i
                                                in user.subscriptions])) \
        .filter(models.Schedule.listing_id == models.Listing.listing_id) \
        .order_by(models.Schedule.date.asc()).all()

    user_schedule_data = []

    for schedule_item in upcoming_schedule:
        air_date = schedule_item[0]
        listing_id = schedule_item[1]
        listing_title = schedule_item[2]

        if date.today() <= air_date.date() and air_date.date() <= (
                date.today() + timedelta(days=7)):
            message = "{} is scheduled to air {}!" \
                .format(
                    listing_title,
                    "today" if air_date.date() == date.today()
                    else "in {} days"
                    .format((air_date.date() - date.today()).days))

            data = {}
            data['listing_id'] = listing_id
            data['time'] = int(time.mktime(air_date.timetuple()))
            data['message'] = message
            user_schedule_data.append(data)

    upcoming_releases = models.Listing.query \
        .filter(
            models.Listing.subscribers.contains(user),
            models.Listing.release_date >= date.today(),
            models.Listing.release_date <= date.today() + timedelta(days=7)) \
        .all()
    for listing in upcoming_releases:
        data = {
            'listing_id': listing.listing_id,
            'time': int(listing.release_date.timestamp()),
            'message': "{} is scheduled to air {} days from now!".format(
                listing.title, (listing.release_date.date() -
                                date.today()).days)
        }
        user_schedule_data.append(data)

    return user_schedule_data
