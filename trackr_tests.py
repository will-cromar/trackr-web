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


class TrackrTestCases(unittest.TestCase):

    # Boilerplate
    def setUp(self):
        # These need to be re-initialized separately for each test because
        # SQLAlchemy is weird
        self.test_people = [
            models.Person(name='Will Cromar'),
            models.Person(name='Alex Marrich'),
            models.Person(name='Brenden Apswich')
        ]

        self.test_listings = [
            models.Listing(title='Biology: Chemistry in Disguise'),
            models.Listing(title='Oviedo: The City of Chickens')
        ]

        self.test_users = [
            models.User(username='will', password='hunter2'),
            models.User(username='alex', password='deadbeef')
        ]

        self.db = db
        self.app = app.test_client()
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    # Tests
    def test_listing_relations(self):
        # Make a copy, since we're mutating its state
        self.db.session.add_all(self.test_listings)
        self.db.session.add_all(self.test_people)
        self.db.session.commit()

        listings = models.Listing.query.all()
        people = models.Person.query.all()
        l = listings[0]
        l.directors.append(people[0])
        l.writers.append(people[1])
        l.actors.extend(people)
        self.db.session.add(l)
        self.db.session.commit()

        listing = listings[0]
        assert listing.directors == [people[0]]
        assert listing.writers == [people[1]]
        assert listing.actors == people

    def test_user_subscriptions(self):
        self.db.session.add_all(self.test_users)
        self.db.session.add_all(self.test_listings)
        self.db.session.commit()

        listings = models.Listing.query.all()
        users = models.User.query.all()
        users[0].subscriptions.extend(listings)
        self.db.session.add(users[0])
        self.db.session.commit()

        users = models.User.query.all()
        assert users[0].subscriptions == listings
        assert users[1].subscriptions == []

    def test_query_api(self):
        self.db.session.add_all(self.test_listings)
        self.db.session.commit()

        listings = models.Listing.query.all()
        resp = self.app.get('/api/query?query=asdf')
        assert json.loads(resp.data) == {'results':
                                         list(map(utils.model_dict, listings))}

    def test_api_create_user(self):
        resp = self.post_json('/api/createaccount', username='will',
                              password='hunter2')
        assert json.loads(resp.data)['status_code'] == "200"
        assert resp.status_code == 200

        resp = self.post_json('/auth', username='will',
                              password='hunter2')
        assert resp.status_code == 200

        token = json.loads(resp.data)['access_token']
        resp = self.get_auth('/api/whoami', authorization=token)
        assert json.loads(resp.data)['username'] == 'will'

    def test_add_subscriptions(self):
        self.db.session.add_all(self.test_listings)
        self.db.session.commit()

        resp = self.post_json('/api/createaccount', username='will',
                              password='hunter2')
        resp = self.post_json('/auth', username='will',
                              password='hunter2')
        assert resp.status_code == 200

        token = json.loads(resp.data)['access_token']

        listings = models.Listing.query.all()
        listing_id = listings[0].listing_id
        resp = self.post_json('/api/addsubscription', authorization=token,
                              listing_id=listings[0].listing_id)

        listing = models.Listing.query.get(listing_id)
        assert resp.status_code == 200
        assert models.User.query.get('will').subscriptions == [listing]

    def test_get_subscriptions(self):
        self.db.session.add_all(self.test_listings)
        self.db.session.commit()

        resp = self.post_json('/api/createaccount', username='will',
                              password='hunter2')
        resp = self.post_json('/auth', username='will',
                              password='hunter2')

        token = json.loads(resp.data)['access_token']
        listings = models.Listing.query.all()
        listing_ids = list(map(lambda l: l.listing_id, listings))
        for lid in listing_ids:
            resp = self.post_json('/api/addsubscription', authorization=token,
                                  listing_id=lid)
            assert resp.status_code == 200

        subs = models.User.query.get('will').subscriptions
        resp = self.get_auth('/api/subscriptions', token)
        assert {'subscriptions': list(map(utils.model_dict, subs))} == (
            json.loads(resp.data))

    # Helpers
    def copy_row(self, item, model):
        """Copies a row, given that row and the constructor for its type"""
        return model(**utils.model_dict(item))

    def get_auth(self, endpoint, authorization=""):
        return self.app.get(endpoint,
                            headers={'Authorization': 'JWT {}'
                                     .format(authorization)})

    def post_json(self, endpoint, authorization="", **kwargs):
        """Post given keywords to endpoint as json"""
        return self.app.post(endpoint, data=json.dumps(kwargs),
                             headers={'Authorization': "JWT {}"
                                      .format(authorization)},
                             content_type='application/json')


if __name__ == "__main__":
    unittest.main()

shutil.rmtree(temp_dir)
