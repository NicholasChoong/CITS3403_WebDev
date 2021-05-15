from flask import render_template, flash, redirect, url_for, request
from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, QuizForm
from app.models import User, Log, Question, Attempt
from werkzeug.urls import url_parse
from datetime import datetime


class UserController:
    def login():
        lform = LoginForm()
        rform = RegistrationForm()  # ??include current user data by default

        if lform.validate_on_submit():  # will return false for a get request
            user = User.query.get(lform.username.data)
            if user is None or not user.check_password(lform.password.data):
                flash("invalid username or password")
                return render_template(
                    "login.html", title="Login", signinform=lform, signupform=rform
                )
            login_user(user, remember=lform.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = "index"
            return redirect(url_for("index"))
        return render_template(
            "login.html", title="Login", signinform=lform, signupform=rform
        )
        # return redirect(url_for('static', filename='login.html'))

    def logout():
        logout_user()
        return redirect(url_for("index"))

    def register():
        form = RegistrationForm()  # ??include current user data by default
        lform = LoginForm()
        if form.validate_on_submit():  # will return false for a GET request
            user = User()
            user.id = form.username.data
            user.set_password(form.new_password.data)
            user.first_name = form.first_name.data
            user.surname = form.surname.data
            if user is None:
                flash("Username is unknown")
                return redirect(url_for("index"))
            if current_user.is_authenticated:
                if not user.check_password(form.password.data):
                    flash("Incorrect password")
                    return redirect(url_for("index"))
            # elif user.password_hash is not None:
            #     flash("User registered")
            #     return redirect(url_for("index"))
            if User.query.get(form.username.data) is not None:
                flash("Username is already taken")
                return render_template(
                    "login.html", title="Register", signupform=form, signinform=lform
                )
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            login_user(user, remember=False)
            return redirect(url_for("index"))
        return render_template(
            "login.html", title="Register", signupform=form, signinform=lform
        )


class ReviewController:
    def get_User_Results():
        Rev = Attempt.query.filter_by(user_id=current_user.id).all()
        return render_template("review.html", title="Review", Res=Rev)


class AttemptController:
    def quiz():
        form = QuizForm()
        if form.validate_on_submit():
            attempt = Attempt(user_id=current_user.id)
            attempt.answer_1 = form.question_1.data
            attempt.answer_2 = form.question_2.data
            attempt.answer_3 = form.question_3.data
            attempt.answer_4 = form.question_4.data
            attempt.answer_5 = form.question_5.data
            attempt.answer_6 = form.question_6.data
            attempt.answer_7 = form.question_7.data
            if attempt is None:
                flash("Invalid Submission")
                return render_template("quiz.html", title="Quiz", form=form)
            db.session.add(attempt)
            db.session.flush()
            db.session.commit()
            AttemptController.mark(attempt.attempt_id)
            return render_template("review.html", title="Review")
        return render_template("quiz.html", title="Quiz", form=form)

    def mark(attempt_id):
        questions = Question.query.all()
        attempt = Attempt.query.get(attempt_id)
        attempt.correct_1 = questions[0].answer == attempt.answer_1
        attempt.correct_2 = questions[1].answer == attempt.answer_2
        attempt.correct_3 = questions[2].answer == attempt.answer_3
        attempt.correct_4 = questions[3].answer == attempt.answer_4
        attempt.correct_5 = questions[4].answer == attempt.answer_5
        attempt.correct_6 = questions[5].answer == attempt.answer_6
        attempt.correct_7 = questions[6].answer == attempt.answer_7
        db.session.commit()


class LogController:
    def get_all_logs():
        pass
