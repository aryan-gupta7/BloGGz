from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
# import random
# import smtplib
import datetime
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    full_name = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(40),nullable=False)
    blogs = db.relationship('Blog',backref='author')
    posts = db.relationship('Post',backref='author')
    def __repr__(self):
        return f'<User {self.full_name}>'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    posts = db.relationship('Post',backref='blog')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self) -> str:
        return f"<Blog '{self.name}'>"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),nullable=False)
    slug = db.Column(db.String(200),nullable=False)
    tagline = db.Column(db.String(500),nullable=False)
    content = db.Column(db.String(2000),nullable=False)
    date_pub = db.Column(db.String(12),nullable=False,default=datetime.datetime.now().strftime("%m/%d/%Y"))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Post '{self.title}'>"
    

# GMAIL_ID = ""
# GMAIL_PSSWD = ""

# def send_mail(to,sub,msg):
#     s = smtplib.SMTP("smtp.gmail.com", 587)
#     s.starttls()
#     s.login(GMAIL_ID, GMAIL_PSSWD)
#     s.sendmail(GMAIL_ID, to, f"Subject: {sub}\n\n{msg}")
#     s.quit()

# def create_otp():
#     nums = [0,1,2,3,4,5,6,7,8,9]
#     otp = f"{random.choice(nums)}{random.choice(nums)}{random.choice(nums)}{random.choice(nums)}"
#     return otp

# def check_otp(correct_otp,entered_otp):
#     return correct_otp == entered_otp

# def send_otp(email,otp):
#     # print(otp)
#     # send_mail(email,"OTP from BloGGz",f"Hey there, your OTP for BloGGz is {otp}")
#     pass

# user = User(username='aryan',email="example@example.com",full_name="Aryan Gupta",password="@aryan77")
# db.session.add(user)
# db.session.commit()


def unique_checker(username,email):
    for user_data in User.query.all():
        if user_data.username==username or user_data.email==email:
            return False
    return True

def check_user(username):
    for users in User.query.all():
        if username == users.username:
            return True
    return False

def check_user_pass(username,password):
    if User.query.filter_by(username=username).first().password == password:
        return True
    else:
        return False

@app.route("/",methods=['GET','POST'])
def main():
    if 'user' not in session:
        if request.method == 'POST':
            name = request.form['full_name']
            username = request.form['username']
            email = request.form['user-email']
            password = request.form['password']
            check_password = request.form['check_password']
            if not password == check_password:
                flash("Entered passwords should match.")
                return redirect(url_for("main"))
            else:
                if unique_checker(username,email):
                    user = User(username=username,email=email,full_name=name.capitalize(),password=password)
                    db.session.add(user)
                    db.session.commit()
                    flash("Registered succesfully!")
                    return redirect(url_for('login'))
                else:
                    flash("Username or email already taken.")
                    return redirect(url_for('main'))
            
        return render_template("index.html")
    else:
        return redirect(url_for('home'))

@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' not in session:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if check_user(username):
                if check_user_pass(username,password):
                    session['user'] = username
                    flash('Logged in succesfully!')
                    return redirect(url_for('home'))
                else:
                    flash('Wrong password provided.')
                    return redirect(url_for('login'))
            else:
                flash("User Not Found.")
                return redirect(url_for('login'))
        return render_template('login.html')
    else:
        return redirect(url_for('home'))

@app.route("/home",methods=['GET','POST'])
def home():
    if 'user' in session:
        if request.method == "POST":
            pass
        return render_template('home.html',user_data=User.query.filter_by(username=session['user']).first())
    else:
        flash("Login in first.")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        flash("Logged out succesfully!")
        return redirect(url_for('login'))
    else:
        return redirect(url_for('main'))


@app.route("/all_blogs")
def all_blogs():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        users_blogs = user.blogs

        return render_template('blogs.html',user=user,users_blogs=users_blogs,no_blogs=len(users_blogs))
    else:
        flash("Log in First!")
        return redirect(url_for('login'))



@app.route("/create_blog",methods=['GET','POST'])
def create_blog():
    if 'user' in session:
        if request.method == 'POST':
            blog_name = request.form['name']
            user = User.query.filter_by(username=session['user']).first()
            new_blog = Blog(name=blog_name,author=user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect(url_for('all_blogs'))
        return render_template('create_blog.html',text='Create')
    else:
        flash("Log in first!")
        return redirect(url_for('login'))

@app.route("/edit_blog/<string:id>",methods=['GET','POST'])
def edit_blog(id):
    if 'user' in session:
        blog = Blog.query.filter_by(id=id).first()
        if request.method == 'POST':
            new_name = request.form['name']
            old_name = blog.name
            if old_name == new_name:
                flash("New name can't be same as old name.")
                return redirect(url_for('edit_blog',id=id))
            else:
                blog.name = new_name
                db.session.add(blog)
                db.session.commit()
                flash("Blog updated succesfully.")
                return redirect(url_for('all_blogs'))
        return render_template('create_blog.html',text='Edit',blog=blog)
    else:
        flash("Login first!")
        return redirect(url_for('login'))


@app.route('/delete_blog/<string:id>')
def delete_blog(id):
    if 'user' in session:
        blog_to_delete = Blog.query.filter_by(id=id).first()
        db.session.delete(blog_to_delete)
        db.session.commit()
        flash("Blog deleted succesfully.")
        return redirect(url_for('all_blogs'))
    else:
        flash('Login first!')
        return redirect(url_for('login'))



@app.route('/create_post/',methods=['POST','GET'])
def create_post():
    if 'user' in session:
        if request.method == 'POST':
            title = request.form['title']
            slug = request.form['slug']
            tagline = request.form['tagline']
            content = request.form['content']
            post = Post(title=title,slug=slug,tagline=tagline,content=content)
            db.session.add(post)
            db.session.commit()
            flash('Posted!')
            return redirect(url_for('all_posts'))
            
        return render_template('create_post.html',text='Create')
    return redirect(url_for('login'))

@app.route('/create_post_in_blog/<string:blog_id>',methods=['GET','POST'])
def create_post_in_blog(blog_id):
    if 'user' in session:
        if request.method == 'POST':
            added_in_blog = Blog.query.filter_by(id=blog_id).first()
            user = User.query.filter_by(username=session['user']).first()
            title = request.form['title']
            slug = request.form['slug']
            tagline = request.form['tagline']
            content = request.form['content']
            post = Post(title=title,slug=slug,tagline=tagline,content=content,blog=added_in_blog,author=user)
            db.session.add(post)
            db.session.commit()
            flash("Posted!")
            return redirect(url_for('all_blogs'))
        return render_template('create_post.html',text='Create')
    else:
        flash("Login first")
        return redirect(url_for('login'))


@app.route("/all_posts")
def all_posts():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        users_posts = user.posts
        return render_template('posts.html',user=user,users_posts=users_posts,no_posts=len(users_posts))
    else:
        flash("Login first!")
        return redirect(url_for('login'))

@app.route("/edit_post/<string:id>",methods=['GET','POST'])
def edit_post(id):
    if 'user' in session:
        post_to_edit = Post.query.filter_by(id=id).first()
        if request.method == 'POST':
            title = request.form['title']
            slug = request.form['slug']
            tagline = request.form['tagline']
            content = request.form['content']
            if post_to_edit.title != title or post_to_edit.slug != slug or post_to_edit.tagline != tagline or post_to_edit.content != content:
                post_to_edit.title = title
                post_to_edit.slug = slug
                post_to_edit.tagline = tagline
                post_to_edit.content = content
                db.session.add(post_to_edit)
                db.session.commit()
                flash("Edited succesfully!")
                return redirect(url_for('all_posts'))
            else:
                flash("Edited details can't be same as old details.")
                return redirect(url_for('edit_post',id=id))
            
        return render_template('create_post.html',text='Edit',post=post_to_edit)
    flash("Login first!")
    return redirect(url_for('login'))

@app.route('/delete_post/<string:id>')
def delete_post(id):
    if 'user' in session:
        post_to_delete = Post.query.filter_by(id=id).first()
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted succesfully.")
        return redirect(url_for('all_blogs'))
    else:
        flash('Login first!')
        return redirect(url_for('login'))


@app.route("/view_blog/<string:id>")
def view_blog(id):
    blog_to_see = Blog.query.filter_by(id=id).first()
    return render_template('blog.html',blog=blog_to_see)

@app.route("/view_post/<string:id>")
def view_post(id):
    post_to_see = Post.query.filter_by(id=id).first()
    return render_template('post.html',post=post_to_see)


if __name__ == "__main__":
    # db.create_all()
    app.run()