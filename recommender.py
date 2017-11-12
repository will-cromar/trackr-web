import math
from app import db, models

"""
    Note: Currently requires a call from within the web server.
    Temporarily add a call to this function through one of the
    routes in views.py to test the output.
"""
def get_recommendations():
    listings = db.session.query(models.Listing).all()

    recommendations = []

    """
        "Et tu, Brute?"
                - CPU
    """

    for l1 in listings:
        top_score = 0
        top_listing = 0

        for l2 in listings:
            t_score, _ = __calc_similarity_score(l1, l2)
            if t_score > top_score and l1 != l2:
                top_score = t_score
                top_listing = l2

        if top_listing != 0:
            recommendations.append((l1.listing_id, top_listing.listing_id))
            print(l1.listing_id, top_score, top_listing.listing_id)

    return recommendations


"""
    Similarity Score is determined by counting the number of
    similar attributes. Generally, higher scores will are preferred.

    listing_1 and listing_2 should be of types models.Listing
"""
def __calc_similarity_score(listing_1, listing_2):

    assert type(listing_1) is models.Listing
    assert type(listing_2) is models.Listing

    genres_1 = listing_1.genres
    genres_2 = listing_2.genres

    actors_1 = listing_1.actors
    actors_2 = listing_2.actors

    writers_1 = listing_1.writers
    writers_2 = listing_2.writers

    directors_1 = listing_1.directors
    directors_2 = listing_2.directors

    scores = [0, 0, 0, 0]

    for genre in genres_1:
        if genre in genres_2:
            scores[0] += 1

    for actor in actors_1:
        if actor in actors_2:
            scores[1] += 1

    for writer in writers_1:
        if writer in writers_2:
            scores[2] += 1

    for director in directors_1:
        if director in directors_2:
            scores[3] += 1

    return sum(scores), scores
