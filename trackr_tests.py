import os
import unittest
import tempfile
import shutil
import json


# This is required because of over-reliance on environment variables.
# Sorry -- Will
temp_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = (
    "sqlite:///" + os.path.join(temp_dir, "app.db"))
from app import app, db, models, utils # noqa
print("Temp database:", app.config['SQLALCHEMY_DATABASE_URI'])


test_people = [
    models.Person(person_id=0, name='Will Cromar'),
    models.Person(person_id=1, name='Alex Marrich'),
    models.Person(person_id=2, name='Brenden Apswich')
]

test_listings = [
    models.Listing(listing_id=0, title='Biology: Chemistry in Disguise'),
    models.Listing(listing_id=1, title='Oviedo: The City of Chickens')
]

test_users = [
    models.User(username='will', password='hunter2'),
    models.User(username='alex', password='deadbeef')
]


class TrackrTestCases(unittest.TestCase):

    # Boilerplate
    def setUp(self):
        self.db = db
        self.app = app.test_client()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    # Tests
    def test_listing_relations(self):
        # Make a copy, since we're mutating its state
        self.db.session.add_all(test_listings)
        self.db.session.add_all(test_people)
        self.db.session.commit()

        listings = models.Listing.query.all()
        people = models.Person.query.all()
        l = listings[0]
        l.directors.append(people[0])
        l.writers.append(people[1])
        l.actors.extend(people)
        self.db.session.add(l)
        self.db.session.commit()

        listing = models.Listing.query.get(0)
        assert listing.directors == [people[0]]
        assert listing.writers == [people[1]]
        assert listing.actors == people

    def test_user_subscriptions(self):
        self.db.session.add_all(test_users)
        self.db.session.add_all(test_listings)
        self.db.session.commit()

        listings = models.Listing.query.all()
        users = models.User.query.all()
        users[0].subscriptions.extend(listings)
        self.db.session.add(users[0])
        self.db.session.commit()

        users = models.User.query.all()
        assert users[0].subscriptions == listings
        assert users[1].subscriptions == []

    def test_api_create_user(self):
        resp = self.post_json('/api/createaccount', username='will',
                              password='hunter2')
        assert json.loads(resp.data)['status_code'] == "200"
        assert resp.status_code == 200

        resp = self.post_json('/auth', username='will',
                              password='hunter2')
        assert resp.status_code == 200

        token = json.loads(resp.data)['access_token']

        resp = self.app.get('/api/whoami',
                            headers={'authorization': 'JWT {}'.format(token)})
        assert json.loads(resp.data)['username'] == 'will'

    def test_query_api(self):
        self.db.session.add_all(test_listings)
        self.db.session.commit()

        listings = models.Listing.query.all()
        resp = self.app.get('/api/query?query=asdf')
        assert json.loads(resp.data) == {'results':
                                         list(map(utils.model_dict, listings))}

    # Helpers
    def copy_row(self, item, model):
        """Copies a row, given that row and the constructor for its type"""
        return model(**utils.model_dict(item))

    def post_json(self, endpoint, authorization="", **kwargs):
        """Post given keywords to endpoint as json"""
        return self.app.post(endpoint, data=json.dumps(kwargs),
                             headers={'authorization': authorization},
                             content_type='application/json')


if __name__ == "__main__":
    unittest.main()

shutil.rmtree(temp_dir)
