import json

import webapp2

routes = [
    (r'/datastore/data/(.*)', 'application.handlers.DataHandler.DataHandler'),
    (r'/datastore/users/(.*)', 'application.handlers.UsersHandler.UsersHandler'),
    (r'/datastore/admin/(.*)', 'application.handlers.AdminHandler.AdminHandler'),
    (r'/(.*)', 'application.handlers.DefaultHandler.DefaultHandler')
]

fp = open('application/configs/application.json', 'r')
config = json.load(fp)

application = webapp2.WSGIApplication(routes=routes, debug=config['debug'], config=config)
