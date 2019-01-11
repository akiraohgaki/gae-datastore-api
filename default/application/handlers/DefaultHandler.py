from application.handlers.BaseHandler import BaseHandler

class DefaultHandler(BaseHandler):

    def get(self, uri=None):
        self.setResponse({'message':'Not found'}, 404)
