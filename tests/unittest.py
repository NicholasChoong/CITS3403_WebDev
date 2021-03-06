import unittest, os
from app import app, db
from app.models import User, Log, Question, Attempt
from app.controllers import (
    UserController,
    LogController,
    AttemptController,
    ReviewController,
)
from datetime import date
from config import Config, TestingConfig


class UnitTest(unittest.TestCase):
    def setUp(self):
        """Setting up."""
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
            basedir, "test.db"
        )
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.app = app.test_client()  # creates a virtual test environment
        db.create_all()
        s1 = User(id="OwO", surname="Case")
        s1.set_password("hello")
        s2 = User(id="wOw", first_name="Unit", surname="Test", isAdmin=True)
        s2.set_password("goodbye")

        t1 = Attempt(user_id="OwO", answer_1="potato", correct_1=True)
        t2 = Attempt(user_id="OwO", answer_1="potato", correct_1=True)
        t3 = Attempt(user_id="wOw", answer_1="potato", correct_1=True)

        q1 = Question(
            question="Who is Steve Jobs?", answer_type="SAQ", answer="Founder of Apple"
        )
        q2 = Question(
            question="Pick 1",
            answer_type="MCQ",
            answer_choice_1="1",
            answer_choice_2="2",
            answer_choice_3="3",
            answer_choice_4="4",
            answer="1",
        )

        l1 = Log(user_id="OwO")
        l2 = Log(user_id="wOw")

        db.session.add(s1)
        db.session.add(s2)
        db.session.add(t1)
        db.session.add(t2)
        db.session.add(t3)
        db.session.add(q1)
        db.session.add(q2)
        db.session.add(l1)
        db.session.add(l2)
        db.session.commit()

        self.assertEqual(app.debug, False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        """Make password hasing works."""
        s = User.query.get("OwO")
        s.set_password("test")
        self.assertFalse(s.check_password("case"))
        self.assertTrue(s.check_password("test"))

    def test_user_is_admin(self):
        """Make sure the role of the user is correctly identified."""
        s = User.query.get("OwO")
        self.assertFalse(s.isAdmin)
        s2 = User.query.get("wOw")
        self.assertTrue(s2.isAdmin)

    def test_attempt(self):
        """Make sure attempt model works."""
        t = Attempt.query.all()
        self.assertEqual(t[0].attempt_id, 1, "Attempt_id should be 1")
        self.assertEqual(t[0].answer_1, "potato", "Asnwer_1 should be potato")
        self.assertTrue(t[0].correct_1)
        self.assertEqual(t[0].user_id, "OwO", "User_id should be OwO")
        u1 = User.query.get("OwO")
        self.assertEqual(
            u1.attempts.filter_by(attempt_id=1).first().attempt_id,
            1,
            "attempt_id from user OwO should be 1",
        )
        self.assertEqual(t[1].attempt_id, 2, "Attempt_id should be 2")
        self.assertEqual(t[2].attempt_id, 3, "Attempt_id should be 3")
        self.assertEqual(t[2].user_id, "wOw", "User_id should be wOw")
        u1 = User.query.get("wOw")
        self.assertEqual(
            u1.attempts.filter_by(attempt_id=3).first().attempt_id,
            3,
            "attempt_id from user wOw should be 1",
        )

    def test_question(self):
        """Make sure question model works."""
        q = Question.query.all()
        self.assertEqual(q[0].question_id, 1, "Quesiton ID should be 1")
        self.assertEqual(q[0].question, "Who is Steve Jobs?")
        self.assertEqual(q[0].answer_type, "SAQ")
        self.assertEqual(q[0].answer, "Founder of Apple")
        self.assertEqual(q[1].question_id, 2, "question id should be 2")
        self.assertEqual(q[1].answer_type, "MCQ")
        self.assertEqual(q[1].answer_choice_1, "1", "Option should be 1")
        self.assertEqual(q[1].answer_choice_2, "2", "Option should be 2")
        self.assertEqual(q[1].answer_choice_3, "3", "Option should be 3")
        self.assertEqual(q[1].answer_choice_4, "4", "Option should be 4")
        self.assertEqual(q[1].answer_choice_4, "4", "Option should be 4")
        self.assertEqual(q[1].answer, "1", "Answer should be 1")

    def test_log(self):
        """Make sure log model works."""
        l = Log.query.all()
        self.assertEqual(l[0].log_id, 1, "Log ID should be 1")
        self.assertEqual(l[0].user_id, "OwO")
        u1 = User.query.get("OwO")
        self.assertEqual(
            u1.logs.filter_by(log_id=1).first().log_id,
            1,
            "log_id from user OwO should be 1",
        )
        self.assertEqual(l[1].log_id, 2, "Log ID should be 2")
        self.assertEqual(l[1].user_id, "wOw")
        u2 = User.query.get("wOw")
        self.assertEqual(
            u2.logs.filter_by(log_id=2).first().log_id,
            2,
            "log_id from user wOw should be 2",
        )

    def test_date(self):
        """Make sure the dates are correct in the models."""
        s = User.query.get("OwO")
        self.assertEqual(s.date.date(), date.today(), "User date is wrong")
        self.assertEqual(
            s.attempts.filter_by(attempt_id=1).first().date.date(),
            date.today(),
            "Date of user's attempt is wrong",
        )
        self.assertEqual(
            s.logs.filter_by(log_id=1).first().date.date(),
            date.today(),
            "Date of user's log is wrong",
        )
        q1 = Question.query.get(1)
        self.assertEqual(
            q1.date.date(),
            date.today(),
            "Date of question is wrong",
        )

    def test_app_exists(self):
        """Make sure the app exists."""
        self.assertFalse(app is None)

    def test_home_page(self):
        """Make sure homepage works."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
