from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz2018@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(12000))
    deleted = db.Column(db.Boolean)
    #timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, owner):
        self.title = title
        self.text = text
        self.deleted = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog',backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # look inside the request to figure out what the user typed
        user_username = request.form['username']
        user_password = request.form['password']
        user = User.query.filter_by(username=user_username).first()
        if user and user.password == user_password:
            session['username']=user_username
            flash('Logged In')
            return redirect('/newpost') 
        #TODO see if redirect is correct
        else:
            flash('User password incorrect or user does not exist','error')
            return render_template('login.html',title = 'Log In',page_title='Log In')

              
    return render_template('login.html',title = 'Log In',page_title='Log In') 
   

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # look inside the request to figure out what the user typed
        user_username = request.form['username']
        user_password = request.form['password']
        user_password_2 = request.form['password2']
        username_exists = User.query.filter_by(username=user_username).first()
                
        error_list = {}

        if (len(user_username)<3) or (len(user_username)>20) or (len(user_username)==0):
            error_list[1] = "Please specify a Username between 3-20 characters long."
                         
        if (len(user_password)<3) or (len(user_password)>20) or (len(user_password)==0):
            error_list[2] = "Please specify a Password between 3-20 characters long."
        
        if user_password != user_password_2:
            error_list[3] = "Passwords do not match."
        
        if username_exists:
           error_list[4] = "Username already exists"

        if error_list:
            return render_template('signup.html',title = 'Sign Up',page_title='Sign Up', username=user_username, errorlist=error_list )

        else:
            new_user = User(user_username,user_password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=user_username
            return redirect ('/newpost') 
                
    return render_template('signup.html',title = 'Sign Up', page_title ='Sign Up', errorlist={} )

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    error_list = {}

    owner=User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_text = request.form['text']
        #blog_owner = User.query.filter_by(username=username).first()

        if len(blog_title)==0:
            error_list[1] = 'Please enter a Blog Title'
        if not blog_text:
            error_list[2] = 'Please enter some text in your blog'
        if error_list:
            return render_template('add_blog.html', title="Add a Blog Entry", page_title="Add a Blog Entry", errorlist=error_list )

        else:
            new_blog = Blog(blog_title, blog_text,owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/post?blog_id=' + str(new_blog.id))

    blogs = Blog.query.filter_by(deleted=False).all()
    
    return render_template('add_blog.html',title="Add a Blog Entry", page_title="Add a Blog Entry",blogs=blogs, errorlist=error_list)

@app.route('/post')
def display():
    
    blog_id = request.args.get('blog_id')
    blog = Blog.query.get(blog_id) #gets the entire row of the table
    blog_title = blog.title
    blog_text= blog.text
    blog_author=blog.owner_id
    blog_author_2 = User.query.join(Blog, blog_author == User.id).all()
    user = User.query.get(blog.owner_id)
    return render_template('display.html',title="Display a Blog", page_title=blog_title, blog_text=blog_text, blog_author=blog_author_2, blog=blog, user=user)

 
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.method == 'GET':
               
        if request.args.get('user_id'):
            author = 'single'
            user_id = request.args.get('user_id')
            user = User.query.get(user_id)
            blogs = Blog.query.join(User, Blog.owner_id == user.id).all()
            return render_template('blog_listing.html',title="All Posts", page_title="Blog Posts by Author", blogs=blogs, user=user, author=author)
        
        else:
            author = ''
            blogs = Blog.query.all()
            users = User.query.join(Blog, User.id == Blog.owner_id).all()
            #users = Blog.query.join(User, User.id == Blog.owner_id ).filter_by(User.id==Blog.owner_id)
            print ('******************')
            print (users, blogs)
            print ('******************')
            return render_template('blog_listing.html',title="All Posts", page_title="All Blog Posts", blogs=blogs, user=users, author=author)
    
@app.route('/', methods=['GET','POST'])
def index():
    users = User.query.all()
    blogs=Blog.query.filter_by(deleted=False).all()
    return render_template('index.html',title="Home", page_title="Blog Users", blogs=blogs, users=users)

@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.deleted = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/blog')
    #not sure the redirect is correct

if __name__ == '__main__':
    app.run()