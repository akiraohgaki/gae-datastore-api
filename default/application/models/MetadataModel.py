from google.appengine.ext import ndb

class MetadataModel(ndb.Model):

    uri = ndb.StringProperty(required=True) # ID
    type = ndb.StringProperty(required=True)
    size = ndb.IntegerProperty(required=True)
    uid = ndb.StringProperty(required=True)
    gid = ndb.StringProperty(required=True)
    mode = ndb.StringProperty(required=True) # File permission bits like 0600
    ctime = ndb.IntegerProperty(required=True) # Epoch time
    mtime = ndb.IntegerProperty(required=True) # Epoch time
    atime = ndb.IntegerProperty(required=True) # Epoch time

    def getEntitiesByUri(self, uri, sort=None):
        '''
        if sort:
            sort = sort.lower()

        if sort == 'uri':
            pass
        elif sort == 'type':
            pass
        elif sort == 'size':
            pass
        elif sort == 'ctime':
            pass
        elif sort == 'mtime':
            pass
        elif sort == 'atime':
            pass
        else:
            pass
        '''
        return self.query(
            self._properties['uri'] >= uri,
            self._properties['uri'] < uri + u'\uFFFD'
        ).order(self._properties['uri']).fetch()
