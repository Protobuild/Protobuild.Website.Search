import webapp2
from google.appengine.ext import ndb
from google.appengine.api import search
import json

class package(ndb.Model):
    name = ndb.StringProperty(required=True);
    description = ndb.StringProperty(required=True);
    googleID = ndb.StringProperty(required=True);

class user(ndb.Model):
    canonicalName = ndb.StringProperty(required=True);
    googleID = ndb.StringProperty(required=True);

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('This is the search endpoint for the Protobuild index.')

class ReindexPackage(webapp2.RequestHandler):
    def get(self, package_id):
        self.response.headers['Content-Type'] = 'application/json'

        package_key = ndb.Key("package", int(package_id))
        package = package_key.get()

        if package == None:
            self.response.write(json.dumps({"error": True, "message": "No such package"}))
            return

        owner = user.gql("WHERE googleID = :id", id=package.googleID).get()

        if owner == None:
            self.response.write(json.dumps({"error": True, "message": "Package has no valid owner"}))
            return

        index = search.Index(name='names-and-descriptions')

        fields = [
            search.TextField(name='name', value=package.name),
            search.TextField(name='description', value=package.description),
            search.AtomField(name='ownerName', value=owner.canonicalName),
        ]

        document = search.Document(doc_id=str(package_id), fields=fields)

        try:
            index.put(document)
            self.response.write(json.dumps({"error": False, "message": "Package re-indexed successfully"}))
        except search.Error:
            self.response.write(json.dumps({"error": True, "message": "Package failed to be indexed"}))

class RemovePackage(webapp2.RequestHandler):
    def get(self, package_id):
        self.response.headers['Content-Type'] = 'application/json'

        package_key = ndb.Key("package", int(package_id))
        package = package_key.get()

        if package != None:
            self.response.write(json.dumps({"error": True, "message": "Package still exists"}))
            return

        index = search.Index(name='names-and-descriptions')

        try:
            index.delete([str(package_id)])
            self.response.write(json.dumps({"error": False, "message": "Package removed from full text search successfully"}))
        except search.Error:
            self.response.write(json.dumps({"error": True, "message": "Package failed to be removed"}))

class SearchPackage(webapp2.RequestHandler):
    def get(self, query):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        index = search.Index(name='names-and-descriptions')
        try:
            search_query = search.Query(query_string=query)
            search_results = index.search(search_query)

            formatted_results = list()
            for doc in search_results:
                info = {"id": int(doc.doc_id)}
                for field in doc.fields:
                    info[field.name] = field.value
                formatted_results.append(info)

            self.response.write(json.dumps({"error": False, "results": formatted_results}))
        except search.Error:
            self.response.write(json.dumps({"error": True, "results": list()}))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/reindex/([0-9]+)', ReindexPackage),
    ('/remove/([0-9]+)', RemovePackage),
    ('/search/(.+)', SearchPackage),
])

