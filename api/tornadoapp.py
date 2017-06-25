import os
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from tornado.httpserver import HTTPServer
from app import app


class MainHandler(RequestHandler):
   def get(self):
       self.redirect(os.environ['SLIDES_URL'])

tr = WSGIContainer(app)

application = Application([
    (r'/nextop/slides', MainHandler),
    (r'.*', FallbackHandler, dict(fallback=tr)),
], autoreload=True)

if __name__ == '__main__':
    server = HTTPServer(application)
    server.bind(80)
    server.start(0)
    IOLoop.current().start()
