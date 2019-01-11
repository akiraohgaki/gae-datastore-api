import time

from google.appengine.ext import ndb

class AccessTokensModel(ndb.Model):

    token = ndb.StringProperty(required=True) # ID
    uid = ndb.StringProperty(required=True)
    expires = ndb.IntegerProperty(required=True) # Epoch time

    def getActiveEntityById(self, id):
        entity = self.get_by_id(id)
        if entity and entity.expires > int(time.time()):
            return entity
        return None
