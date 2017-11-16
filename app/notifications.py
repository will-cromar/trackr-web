from datetime import date, datetime, timedelta
from app import db, models
import .recommender
import random


'''
    Returns a JSON of all recommendation and schedule notifications
'''
def get_notifications():


    notification_dict = {}
    notification_dict['recommendations'] = __fetch_recommendation_data()
    notification_dict['schedules'] = __fetch_schedule_data()

    return notification_dict


'''
    Gathers a list of recommendations (1 per user) and returns a dictionary of that data
'''
def __fetch_recommendation_data():

    recommendation_data = []

    users = db.session.query(models.User).all()

    for user in users:

        subs = user.subscriptions

        if len(subs) <= 0:
            continue

        rand_listing = subs[random.randint(0, len(subs) - 1)]

        username = user.username
        source_title = rand_listing.title

        recommendation = recommender.get_closest_recommendation(rand_listing)

        if recommendation is None:
            continue

        recommendation_title = recommendation.title

        message = "Based on your interest in {}, we recommend you try {}!".format(source_title, recommendation_title)

        t_data = {}
        t_data['source_id'] = rand_listing.listing_id
        t_data['recommendation_id'] = recommendation.listing_id
        t_data['message'] = message

        data = {}
        data[user.username] = t_data

        recommendation_data.append(data)

    return recommendation_data

'''
    Gathers a list of Schedule data per user and returns a dictionary of that data
'''
def __fetch_schedule_data():

    users = db.session.query(models.User).all()

    schedule_data = []

    for user in users:

        upcoming_schedule = db.session.query(models.Schedule.date, models.Schedule.listing_id, models.Listing.title).\
                            filter(models.Schedule.listing_id.in_([i.listing_id for i in user.subscriptions])).\
                            filter(models.Schedule.listing_id == models.Listing.listing_id).\
                            order_by(models.Schedule.date.asc()).all()

        user_schedule_data = []

        for schedule_item in upcoming_schedule:
            air_date = schedule_item[0].date()
            listing_id = schedule_item[1]
            listing_title = schedule_item[2]

            if date.today() <= air_date and air_date <= (date.today() + timedelta(days=365)):
                message = "{} is scheduled to air {}!".format(listing_title, \
                    "today" if air_date == date.today() else "in {} days".\
                    format((air_date - date.today()).days))

                data = {}
                data['listing_id'] = listing_id
                data['datetime'] = air_date
                data['message'] = message
                #u_time = unix_time(air_date)
                user_schedule_data.append(data)

        schedule_dict = {}
        schedule_dict[user.username] = user_schedule_data
        schedule_data.append(schedule_dict)

    return schedule_data
