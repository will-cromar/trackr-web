from datetime import date, datetime, timedelta
from app import db, models
from .recommender import get_closest_recommendation
import random
import time


'''
    Returns a JSON of all recommendation and schedule notifications
'''
def get_notifications():
    notification_dict = {}

    users = db.session.query(models.User).all()

    for user in users:
        recommendations = __fetch_recommendation_data(user)
        reminders = __fetch_schedule_data(user)
        notification_dict[user.username] = recommendations + reminders

    return notification_dict


'''
    Gathers a list of recommendations (1 per user) and returns a dictionary of that data
'''
def __fetch_recommendation_data(user):
    recommendation_data = []

    subs = user.subscriptions

    if len(subs) <= 0:
        return {}

    rand_listing = subs[random.randint(0, len(subs) - 1)]

    username = user.username
    source_title = rand_listing.title

    recommendation = get_closest_recommendation(rand_listing)

    if recommendation is None:
        return {}

    recommendation_title = recommendation.title

    # message = "Based on your interest in {}, we recommend you try {}!".format(source_title, recommendation_title)

    t_data = {}
    t_data['listing_id'] = recommendation.listing_id
    t_data['time'] = int(recommendation.release_date.timestamp())
    t_data['message'] = "We recommend you try {}!".format(recommendation_title)
    t_data['submessage'] = "Based on your interest in {}".format(source_title)

    return [t_data]


'''
    Gathers a list of Schedule data per user and returns a dictionary of that data
'''
def __fetch_schedule_data(user):

    upcoming_schedule = db.session.query(models.Schedule.date, models.Schedule.listing_id, models.Listing.title).\
                        filter(models.Schedule.listing_id.in_([i.listing_id for i in user.subscriptions])).\
                        filter(models.Schedule.listing_id == models.Listing.listing_id).\
                        order_by(models.Schedule.date.asc()).all()

    user_schedule_data = []

    for schedule_item in upcoming_schedule:
        air_date = schedule_item[0]
        listing_id = schedule_item[1]
        listing_title = schedule_item[2]

        if date.today() <= air_date.date() and air_date.date() <= (date.today() + timedelta(days=365)):
            message = "{} is scheduled to air {}!".format(listing_title, \
                "today" if air_date.date() == date.today() else "in {} days".\
                format((air_date.date() - date.today()).days))

            data = {}
            data['listing_id'] = listing_id
            data['time'] = int(time.mktime(air_date.timetuple()))
            data['message'] = message
            user_schedule_data.append(data)

    return user_schedule_data
