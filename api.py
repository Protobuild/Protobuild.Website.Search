import webapp2
from google.appengine.ext import ndb

class package(ndb.Model):
    name = ndb.StringProperty(required=True);
    description = ndb.StringProperty(required=True);

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('This is the search endpoint for the Protobuild index.')

class ReindexPackage(webapp2.RequestHandler):
    def get(self, package_id):
        self.response.headers['Content-Type'] = 'text/plain'

        package_key = ndb.Key("package", int(package_id))
        package = package_key.get()

        if package == None:
            self.response.write("No such package")
            return

        self.response.write(package.name + "\n")
        self.response.write(package.description + "\n")
        pass

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/reindex/([0-9]+)', ReindexPackage),
], debug=True)

