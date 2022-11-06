import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,LoginManager,UserMixin,logout_user,login_required,current_user
from datetime import datetime



base_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, "blog_project.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'baea6b05b5000471335e'


db = SQLAlchemy(app)
login_manager = LoginManager(app)

# UserMixin is used to check if the user is active or not
# Creating the user and blog post schema
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.Text, nullable=False)

class Blogposts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    post = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Blogpost {self.id}"

with app.app_context():
    db.init_app(app)
    db.create_all()

@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.route('/')
def blog_home():
    blogs = Blogposts.query.all()
    return render_template("index.html", blogs=blogs)


@app.route("/login", methods=['GET','POST'])
def login():
    username = request.form.get("username")
    # username = username.title()
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()


    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('blog_home'))

    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user_username = request.form.get("username")
        user_fullname = request.form.get("fullname")
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        # user_confirm_password = request.form.get("confirm")

        password_hash = generate_password_hash(user_password)

        new_user = User(username=user_username, email=user_email, full_name=user_fullname, password=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("signup.html")


@app.route('/post', methods=['GET', 'POST'])
def post_a_blog():
    if request.method == "POST":
        blog_title = request.form.get("Title")
        blog_post = request.form.get("blogposts")
        theauthor = current_user.username
        date = datetime.now()
        date = date.replace(microsecond=0)
        # time = datetime.now().time().replace(microsecond=0)
        # # date = datetime.now()


        new_blog = Blogposts(title=blog_title, post=blog_post, author=theauthor, date_posted=date)

        db.session.add(new_blog)
        db.session.commit()

        return redirect(url_for('blog_home'))

    return render_template("post.html")

@app.route('/blog/<int:id>')
def get_blog(id):
    blog = Blogposts.query.filter_by(id=id).first()
    return render_template("blog.html", blog=blog)


@app.route("/post/edit/<int:id>", methods=['GET','POST'])
def edit_post(id):
    post = Blogposts.query.get_or_404(id)

    if request.method == "POST":
        post.title = request.form.get("title")
        post.post = request.form.get("blogposts")
        db.session.commit()

        flash("Your post has been edited", category="success")
        return redirect(url_for('blog_home'))

    return render_template("edit.html", post=post)


@app.route("/delete/<int:id>", methods=['GET'])
def delete_post(id):
    post_to_delete = Blogposts.query.get_or_404(id)

    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('blog_home'))

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/about-me')
def about_me():
    return render_template("about.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('blog_home'))


# @app.route('/protected')
# @login_required
# def protected():
#     return render_template('protected.html')


if __name__ == "__main__":
    app.run(debug=True)
