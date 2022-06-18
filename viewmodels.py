from models import User, db, BlogPost, Comment
from flask_login import login_user, current_user
from flask import flash
from werkzeug.security import generate_password_hash, check_password_hash


class PostViewModel:

    def __init__(self, method, post_id):
        self.method = method
        self.post_id = post_id
        self.requested_post = BlogPost.query.get(post_id)

    def fetch_comments(self, form, comment_id):

        if self.method == "POST":
            if not comment_id:
                new_comment = Comment(
                    text=form.get('comment-text'),
                    comment_author=current_user,
                    parent_post=self.requested_post
                )
                db.session.add(new_comment)
                db.session.commit()
            else:
                requested_comment = Comment.query.get(comment_id)
                new_answer = Comment(
                    text=form.get('comment-text'),
                    comment_author=current_user,
                    parent_post=self.requested_post,
                    parent_comment=requested_comment
                )
                db.session.add(new_answer)
                db.session.commit()

    def get_requested_post(self):
        return self.requested_post


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
