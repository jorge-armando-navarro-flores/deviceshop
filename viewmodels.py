from models import User, db
from flask_login import login_user, current_user
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash


class LoginViewModel:

    def __init__(self, form, method):
        self.form = form
        self.method = method
        self.redirect = "home"
        self.login_success = False

    def check_username(self):
        if self.method == "POST":
            email = self.form.get('email')
            password = self.form.get('password')
            page = self.form.get('page')
            print(page)
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("That email does not exist, please try again.")
                self.redirect = "register"
            elif not check_password_hash(user.password, password):
                flash('Password incorrect, please try again.')
                self.redirect = "login"
            else:
                self.login_success = True
                login_user(user)

    def get_redirect_page(self):
        return self.redirect

    def get_login_success(self):
        return self.login_success
