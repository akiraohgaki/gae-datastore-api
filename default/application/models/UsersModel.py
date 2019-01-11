from google.appengine.ext import ndb

class UsersModel(ndb.Model):

    uid = ndb.StringProperty(required=True) # ID
    gids = ndb.StringProperty(required=True) # Comma-separated list
    username = ndb.StringProperty(required=True)
    active = ndb.IntegerProperty(required=True) # 1|0

    def getActiveEntityById(self, id):
        entity = self.get_by_id(id)
        if entity and entity.active == 1:
            return entity
        return None

    def getActiveEntityByUsername(self, username):
        return self.query(
            self._properties['username'] == username,
            self._properties['active'] == 1
        ).get()

    def getActiveEntities(self):
        return self.query(self._properties['active'] == 1).fetch()
