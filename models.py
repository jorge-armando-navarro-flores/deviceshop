from flask_login import UserMixin
from sqlalchemy.orm import relationship
from __init__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

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
