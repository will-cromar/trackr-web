from hashlib import sha256
import string
import random


def passwordHash(password):
    passwordBytes = password.encode('utf-8')
    return sha256(passwordBytes).hexdigest()


def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def generate_random_listings(num_listings=10, num_people=20, string_length=20):
    """Generates random listings given number of listings, number of people,
    and the length of random strings."""
    peopleNames = [random_string(string_length) for _ in range(num_people)]
    people = [{'personId': i, 'name': name}
              for i, name in enumerate(peopleNames)]

    listings = [
        {
            'title': random_string(string_length),
            'description': random_string(string_length) * 10,
            # Date ranges are arbitrary
            'releaseDate': random.randint(1506816000, 1512086400),
            'actors': list(random.choices(people, k=5)),
            'writers': [random.choice(people)],
            'directors': [random.choice(people)],
            'genres': [{'genreId': 1, 'genre': 'fake'}],
        }
        for _ in range(num_listings)
    ]

    return listings
