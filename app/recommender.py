from app import db, models
import numpy as np
from sklearn.cluster import AffinityPropagation

"""
    Note: Currently requires a call from within the web server.
    Temporarily add a call to this function through one of the
    routes in views.py to test the output.
"""
def get_recommendations():
    listings = db.session.query(models.Listing).all()

    recommendations = []

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

def get_closest_recommendation(listing_1):
    listings = db.session.query(models.Listing).all()

    top_score = 0
    top_listing = None

    for l1 in listings:
        t_score, _ = __calc_similarity_score(listing_1, l1)
        if t_score > top_score and listing_1 != l1:
            top_score = t_score
            top_listing = l1

    return top_listing


def get_neighbors(listings, target_idx=-1):
    """Returns a list of listings similar to the one at target_idx."""
    clusters = get_affinity_clusters(listings)
    target_cluster = clusters[target_idx]

    res = []
    for listing, cid in zip(listings, clusters):
        if cid == target_cluster and listing != listings[target_idx]:
            res.append(listing)

    return res


def get_affinity_clusters(listings):
    """Returns a list of cluster IDs based on relative similarity between
    listings."""
    a = get_similarity_matrix(listings)

    clf = AffinityPropagation(affinity='precomputed')
    clusters = clf.fit_predict(a)

    return clusters


def get_similarity_matrix(listings):
    """Returns a numpy matrix of the affinities between listings."""
    n = len(listings)
    m = np.zeros((n, n))

    for i, l1 in enumerate(listings):
        for j, l2 in enumerate(listings):
            m[i, j] = __calc_similarity_score(l1, l2)[0]

    return m


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
