from google.appengine.ext import ndb

class DataModel(ndb.Model):

    data = ndb.BlobProperty(required=True, indexed=False)
