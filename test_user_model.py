"""User model tests."""
 
# run these tests like:
#
#    python -m unittest test_user_model.py
 
 
import os
from unittest import TestCase
from sqlalchemy import exc
 
from models import db, User, Message, Follows
 
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
 
 
class UserModelTestCase(TestCase):
    """Test views for messages."""
 
    def setUp(self):
        """Create test client, add sample data."""
 
        #User.query.delete()
        #Message.query.delete()
        #Follows.query.delete()
        db.drop_all()
        db.create_all()
 
        u1 = User.signup("test_user_1", "1@email.com", "password", None)
        u1id = 11
        u1.id = u1id
 
        u2 = User.signup("test_user_2", "2@email.com", "password", None)
        u2id = 22
        u2.id = u2id
 
        db.session.commit()
 
        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)
 
        self.u1 = u1
        self.u1id = u1id
        self.u2 = u2
        self.u2id = u2id
 
        self.client = app.test_client()
 
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
 
 
    def test_user_model(self):
        """Does basic model work?"""
 
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
 
        db.session.add(u)
        db.session.commit()
 
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
 
 
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()
 
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)
 
        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)
 
    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()
 
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))
 
    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()
 
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
 
    def test_signup(self):
        u3 = User.signup("test_user_3", "3@email.com", "password", None)
        u3id = 33
        u3.id = u3id
        db.session.commit()
 
        u3 = User.query.get(u3id)
        self.assertIsNotNone(u3)
        self.assertEqual(u3.username, "test_user_3")
        self.assertEqual(u3.email, "3@email.com")
        self.assertNotEqual(u3.password, "password")
 
    def test_invalid_email(self):
        email = User.signup("user", None, "password", None)
        uid = 44
        email.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
 
    def test_invalid_name(self):
        name = User.signup(None, "test@email.com", "password",None)
        uid = 55
        name.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
 
    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
 
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1id)
    
    def test_wrong_name(self):
        self.assertFalse(User.authenticate("badusername", "password"))
 
    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

