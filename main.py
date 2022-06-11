from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from datetime import date
from purchase import MadePurchase

from sqlalchemy import func
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, EditProductForm, EditUserForm
from flask_gravatar import Gravatar

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deviceshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # ***************Child Relationship*************#
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    purchases = relationship("Purchase", back_populates="user_purchase")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)

    # ***************Parent Relationship*************#
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # ***************Child Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)

    # ***************Parent Relationship*************#
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

    text = db.Column(db.Text, nullable=False)


Comment.comment_id = db.Column(db.Integer, db.ForeignKey(Comment.id))
Comment.parent_comment = relationship(Comment, backref="answers", remote_side=Comment.id)


class Purchase(db.Model):
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)

    # ***************Parent Relationship*************#
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_purchase = relationship("User", back_populates="purchases")

    date = db.Column(db.String(250))
    purchase_total = db.Column(db.Integer)

    # ***************Child Relationship*************#
    orders = relationship('Order', back_populates="purchase")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)

    # ***************Parent Relationship*************#
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'))
    purchase = relationship("Purchase", back_populates="orders")
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = relationship("Product", back_populates="orders")


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    price = db.Column(db.Integer)
    img_url = db.Column(db.String(250), nullable=False)

    # ***************Child Relationship*************#
    orders = relationship('Order', back_populates="product")


# Line below only required once, when creating DB.


db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise, continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    posts = BlogPost.query.all()
    all_products = Product.query.all()
    return render_template("index.html", all_posts=posts, all_products=all_products)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["POST", "GET"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("blog_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/blog-home")
def blog_home():
    return render_template("blog-home.html")


@app.route("/blog-post/<int:post_id>", methods=["GET", "POST"], defaults={'comment_id': None})
@app.route("/blog-post/<int:post_id>/<int:comment_id>", methods=["GET", "POST"])
def blog_post(post_id, comment_id):
    requested_post = BlogPost.query.get(post_id)
    if request.method == "POST":
        if not comment_id:
            new_comment = Comment(
                text=request.form.get('comment-text'),
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
        else:
            requested_comment = Comment.query.get(comment_id)
            new_answer = Comment(
                text=request.form.get('comment-text'),
                comment_author=current_user,
                parent_post=requested_post,
                parent_comment=requested_comment
            )
            db.session.add(new_answer)
            db.session.commit()
            # redirect(url_for('home'))

    return render_template("blog-post.html", post=requested_post, visited=set())


@app.route("/portfolio-overview")
def portfolio_overview():
    return render_template("portfolio-overview.html")


@app.route("/portfolio-item")
def portfolio_item():
    return render_template("portfolio-item.html")


@app.route("/admin")
@admin_only
def admin():
    return render_template("admin.html")


@app.route("/tables")
def tables():
    return render_template("tables.html")


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
            login_user(new_user)
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
        page = request.form.get('page')
        print(page)

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
            # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('blog_post'))
        else:
            login_user(user)
            return redirect(page)

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


@app.route("/products", methods=["GET", "POST"], defaults={'operation': None, 'item_id': None})
@app.route("/products/<operation>/<int:item_id>", methods=["GET", "POST"])
def products(operation, item_id):
    if request.method == "POST" and not operation:
        new_product = Product(
            name=request.form.get('name'),
            brand=request.form.get('brand'),
            price=request.form.get('price'),
            img_url=request.form.get("img_url"),
        )

        db.session.add(new_product)
        db.session.commit()
    elif operation == "DELETE":
        product_to_delete = Product.query.get(item_id)
        if product_to_delete:
            db.session.delete(product_to_delete)
            db.session.commit()
        return redirect(url_for('products'))
    elif operation == "EDIT":
        product = Product.query.get(item_id)
        edit_form = EditProductForm(
            name=product.name,
            brand=product.brand,
            price=product.price,
            img_url=product.img_url

        )
        if edit_form.validate_on_submit():
            product.name = edit_form.name.data
            product.brand = edit_form.brand.data
            product.price = edit_form.price.data
            product.img_url = edit_form.img_url.data
            db.session.commit()
            return redirect(url_for('products'))

        return render_template("edit.html", form=edit_form)

    all_products = Product.query.all()

    return render_template("tables.html", items=all_products, model=Product)


@app.route("/users", methods=["GET", "POST"], defaults={'operation': None, 'item_id': None})
@app.route("/users/<operation>/<int:item_id>", methods=["GET", "POST"])
def users(operation, item_id):
    if request.method == "POST" and not operation:
        new_user = User(
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password'),
        )

        db.session.add(new_user)
        db.session.commit()
    elif operation == "DELETE":
        user_to_delete = User.query.get(item_id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
        return redirect(url_for('users'))
    elif operation == "EDIT":
        user = User.query.get(item_id)
        edit_form = EditUserForm(
            username=user.username,
            email=user.email,
            password=user.password,
        )

        if edit_form.validate_on_submit():
            user.username = edit_form.username.data
            user.email = edit_form.email.data
            user.password = edit_form.password.data
            db.session.commit()
            return redirect(url_for('users'))

        return render_template("edit.html", form=edit_form)

    all_users = User.query.all()

    return render_template("tables.html", items=all_users, model=User)


@app.route("/remove-from-cart")
def remove_from_cart():
    product_id = request.args.get('product_id')
    order_to_delete = Order.query.filter_by(product_id=product_id).first()
    db.session.delete(order_to_delete)
    db.session.commit()
    return redirect(url_for("cart"))


@app.route("/add-to-cart")
def add_to_cart():
    product_id = request.args.get('product_id')
    current_product = Product.query.filter_by(id=product_id).first()
    purchase_id = db.session.query(func.max(Purchase.id)).filter_by(user_purchase=current_user).scalar()
    if not purchase_id:
        new_purchase = Purchase(
            user_purchase=current_user
        )
        db.session.add(new_purchase)
        db.session.commit()
    purchase_id = db.session.query(func.max(Purchase.id)).filter_by(user_purchase=current_user).scalar()
    current_purchase = Purchase.query.filter_by(id=purchase_id).first()

    new_order = Order(
        purchase=current_purchase,
        product=current_product
    )
    db.session.add(new_order)
    db.session.commit()

    print(current_product)
    print(current_purchase)

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    # order = Order.query.filter_by(id=1).first()
    # print(order.product)
    # count = db.session.query(Order.product, func.count(Order.product)).group_by(Order.product).all()
    # print(count)
    purchase_id = db.session.query(func.max(Purchase.id)).filter_by(user_purchase=current_user).scalar()
    cart_items = db.session.query(func.count(Order.id), Product) \
        .select_from(Product).join(Order).group_by(Product.id).filter_by(purchase_id=purchase_id).all()

    return render_template("cart.html", items=cart_items)


@app.route("/purchase")
def purchase():
    purchase_id = db.session.query(func.max(Purchase.id)).filter_by(user_purchase=current_user).scalar()
    current_purchase = Purchase.query.filter_by(id=purchase_id).first()

    total = 0
    for order in current_purchase.orders:
        total += order.product.price
    current_purchase.date = date.today()
    current_purchase.purchase_total = total

    new_purchase = Purchase(
        user_purchase=current_user,
    )

    db.session.add(new_purchase)
    db.session.commit()

    return redirect(url_for('my_shopping'))


@app.route("/my-shopping")
def my_shopping():
    all_purchases = Purchase.query.filter_by(user_purchase=current_user)
    purchases = []
    for item in all_purchases:
        print(item.id)
        purchase_products = db.session.query(func.count(Order.id), Product) \
            .select_from(Product).join(Order).group_by(Product.id).filter_by(purchase_id=item.id).all()
        purchases.append(MadePurchase(purchase_products, item.date, item.purchase_total))
        print(purchase_products)

    return render_template("my-shopping.html", purchases=purchases)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
