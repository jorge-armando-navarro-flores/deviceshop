from flask import Flask, render_template, redirect, url_for, flash

app = Flask(__name__)


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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")


@app.route("/products-search")
def products_search():
    return render_template("products-search.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")





if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

