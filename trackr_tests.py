import os
import unittest
import tempfile
import shutil
from app import app, db, models, utils


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
        self.temp_dir = tempfile.mkdtemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            "sqlite:///" + os.path.join(self.temp_dir, "app.db"))
        self.db = db
        self.app = app.test_client()
        with app.app_context():
            self.db.create_all()

    def tearDown(self):
        self.db.drop_all()
        shutil.rmtree(self.temp_dir)

    # Tests
    def test_listing_relations(self):
        # Make a copy, since we're mutating its state
        l = self.copy_row(test_listings[0], models.Listing)
        l.directors.append(test_people[0])
        l.writers.append(test_people[1])
        l.actors.extend(test_people)
        self.db.session.add(l)
        self.db.session.commit()

        listing = models.Listing.query.get(0)
        people = models.Person.query.all()
        assert listing.directors == [people[0]]
        assert listing.writers == [people[1]]
        assert listing.actors == people

    def test_user_subscriptions(self):
        u = self.copy_row(test_users[0], models.User)
        u.subscriptions.extend(test_listings)
        self.db.session.add(u)
        self.db.session.add(test_users[1])
        self.db.session.commit()

        users = models.User.query.all()
        listings = models.Listing.query.all()
        assert users[0].subscriptions == listings
        assert users[1].subscriptions == []

    # Helpers
    def copy_row(self, item, model):
        """Copies a row, given that row and the constructor for its type"""
        return model(**utils.model_dict(item))


if __name__ == "__main__":
    unittest.main()