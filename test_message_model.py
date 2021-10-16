"""Message model tests."""
 
# run these tests like:
#
#    python -m unittest test_message_model.py
 
 
import os
from unittest import TestCase
from sqlalchemy import exc
 
from models import db, User, Message, Follows, Likes
 
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
 
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
 
 
# Now we can import app
 
from app import app
 
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
 
db.create_all()
 
 
class MessageModelTestCase(TestCase):
    """Test views for messages."""
 
    def setUp(self):
        """Create test client, add sample data."""
 
        #User.query.delete()
        #Message.query.delete()
        #Follows.query.delete()
        db.drop_all()
        db.create_all()
 
        u1 = User.signup("test_user_1", "1@email.com", "password", None)
        self.u1id = 11
        u1.id = self.u1id
 
        db.session.commit()

        self.u1 = User.query.get(self.u1id)
 
        self.client = app.test_client()
 
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
 
    def test_message_model(self):

        m = Message(text="test", user_id=self.u1id)

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "test")

    def test_message_likes(self):

        m = Message(text="test", user_id=self.u1id)
        u2 = User.signup("test_user_2", "2@email.com", "password", None)
        u2id = 22
        u2.id = u2id
        u2.likes.append(m)
        db.session.add_all([m, u2])
        db.session.commit()

        l = Likes.query.filter(Likes.user_id == u2id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id,m.id)

