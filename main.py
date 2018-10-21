from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog2018@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    text = db.Column(db.String(12000))
    deleted = db.Column(db.Boolean)

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.deleted = False


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    error_list = {}

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_text = request.form['text']
        if len(blog_title)==0:
            error_list[1] = 'Please enter a Blog Title'
        if not blog_text:
            error_list[2] = 'Please enter some text in your blog'
        if error_list:
            return render_template('add_blog.html', title="Add a Blog Entry", page_title="Add a Blog Entry", errorlist=error_list )

        else:
            new_blog = Blog(blog_title, blog_text)
            db.session.add(new_blog)
            db.session.commit()
            
            return redirect('/post?blog_id=' + str(new_blog.id))

    blogs = Blog.query.filter_by(deleted=False).all()
    
    return render_template('add_blog.html',title="Add a Blog Entry", page_title="Add a Blog Entry",
        blogs=blogs, errorlist=error_list)

@app.route('/post')
def display():
    
    blog_id = request.args.get('blog_id')
    blog = Blog.query.get(blog_id) #gets the entire row of the table
    blog_title = blog.title
    blog_text= blog.text

    return render_template('display.html',title="Display a Blog", page_title=blog_title, blog_text=blog_text)

 
@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_text = request.form['text']
        new_blog = Blog(blog_title, blog_text)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.filter_by(deleted=False).all()
    deleted_blogs = Blog.query.filter_by(deleted=True).all()
    return render_template('blog_listing.html',title="Build a Blog", page_title="Build a Blog",
        blogs=blogs)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    blog.deleted = True
    db.session.add(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()