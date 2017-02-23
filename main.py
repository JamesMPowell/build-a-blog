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
    def render_front(self, title="", blog="",error="",offset = 0, page = 0, prev_page = 0, next_page = 0):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC limit 5 offset " +str(offset))
        counter = blogs.count(offset=offset)
        if page == None or page == 1:    
            self.render("next_button.html", title=title, blog=blog, error=error, blogs = blogs, page = page, prev_page = prev_page,next_page = next_page)
        elif counter < 5:
            self.render("prev_button.html", title=title, blog=blog, error=error, blogs = blogs, page = page, prev_page = prev_page,next_page = next_page)
        else:
            self.render("both_button.html", title=title, blog=blog, error=error, blogs = blogs, page = page, prev_page = prev_page,next_page = next_page)
               
         
    def get(self):
        page_num = self.request.get("page")
        prev_page = 0
        page = 1
        offset = 0
        next_page = 2
        if page_num and page_num.isdigit:
            page_num = int(page_num)
            offset= 5*(page_num-1)
            if page_num != 1:
                page = page_num+1
            next_page = (page_num +1) 
            prev_page = (page_num -2)
        self.render_front(offset = offset, page = page, prev_page = prev_page,next_page = next_page)
        
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
            b = Blog(title = title, blog = blog)
            b.put()
            self.redirect("/")
        else:   
            error = "we need both a title and some content!"
            self.render_front(title,blog, error)   
class ViewPostHandler(Handler):
    def get(self,id):
        #self.response.write(id)  #Prints the id number
        blog_post = Blog.get_by_id(int(id))
        self.render("blog_post.html" , blog_post = blog_post) 

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog',MainHandler),
    ('/newpost',NewPost),
    webapp2.Route('/blog/<id:\d+>',ViewPostHandler)
], debug=True)
