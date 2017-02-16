import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a,**kw):
        self.response.out.write(*a,**kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

class Blog(db.Model):
    title= db.StringProperty(required=True)
    blog= db.TextProperty(required=True)
    created= db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", blog="",error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5")
        self.render("front_page.html", title=title, blog=blog, error=error, blogs = blogs)
         
    def get(self):
        self.render_front()

    

class RecentPosts(Handler):
    def render_front(self,  blog=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5")
        self.render("front_page.html", blogs = blogs, blog = blog)
         
    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_front(self, title="", blog="",error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5")
        self.render("new_post.html", title=title, blog=blog, error=error)
         
    def get(self):
        self.render_front() 

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()

            self.redirect("/")
        else:   
            error = "we need both a title and some content!"
            self.render_front(title,blog, error)   
class ViewPostHandler(Handler):
    def render_front(self,  blog=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5") 
        self.render("blog_post.html",  blog = blog)
         
    def get(self):
        self.render_front()  

class get_posts(limit,offset):  
    def render_front(self):
        blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC") 
        return blog_posts
    def get(self):
        self.render_front()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog',RecentPosts),
    ('/newpost',NewPost),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
