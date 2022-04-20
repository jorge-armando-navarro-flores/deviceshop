from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# CREATE TABLE IN DB


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# Line below only required once, when creating DB.
db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/blog-home")
def blog_home():
    return render_template("blog-home.html")


@app.route("/blog-post")
def blog_post():
    return render_template("blog-post.html")


@app.route("/portfolio-overview")
def portfolio_overview():
    return render_template("portfolio-overview.html")


@app.route("/portfolio-item")
def portfolio_item():
    return render_template("portfolio-item.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        email = request.form.get('email')
        if not User.query.filter_by(email=email).first():
            new_user = User(
                username=request.form.get('username'),
                email=email,
                password=hash_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
            # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")


@app.route("/products-search")
def products_search():
    return render_template("products-search.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/my-shopping")
def my_shopping():
    return render_template("my-shopping.html")





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

