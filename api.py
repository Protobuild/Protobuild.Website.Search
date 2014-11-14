import webapp2
from google.appengine.ext import ndb
from google.appengine.api import search

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

        index = search.Index(name='names-and-descriptions')

        fields = [
            search.TextField(name='name', value=package.name),
            search.TextField(name='description', value=package.description),
        ]

        document = search.Document(doc_id=str(package_id), fields=fields)

        try:
            index.put(document)
            self.response.write("Package re-indexed successfully")
        except search.Error:
            self.response.write("Package failed to be indexed")

class SearchPackage(webapp2.RequestHandler):
    def get(self, query):
        self.response.headers['Content-Type'] = 'application/json'

        index = search.Index(name='names-and-descriptions')
        try:
            search_query = search.Query(query_string=query)
            search_results = index.search(search_query)
            self.response.write('{"error": false, "results": []}')
        except search.Error:
            self.response.write('{"error": true, "results": []}')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/reindex/([0-9]+)', ReindexPackage),
    ('/search/(.+)', SearchPackage),
], debug=True)

