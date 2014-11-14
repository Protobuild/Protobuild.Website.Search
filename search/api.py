import webapp2

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('This is the search endpoint for the Protobuild index.')

application = webapp2.WSGIApplication([
    ('/', MainPage)
])

