import os
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from app import app


class MainHandler(RequestHandler):
   def get(self):
       self.redirect(os.environ['SLIDES_URL'])

tr = WSGIContainer(app)

application = Application([
    (r'/nextop/slides', MainHandler),
    (r'.*', FallbackHandler, dict(fallback=tr)),
])

if __name__ == '__main__':
    application.listen(80)
    IOLoop.instance().start()
