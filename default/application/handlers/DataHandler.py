from application.handlers.BaseHandler import BaseHandler

from application.models.MetadataModel import MetadataModel
from application.models.DataModel import DataModel

class DataHandler(BaseHandler):

    isAuthRequired = True

    def getAction(self, uri=None):
        # Parameters:
        # metadata=1|0
        # sort=name|type|size|ctime|mtime|atime
        if self.isResourcePath(uri):
            metadataModel = MetadataModel()
            metadataEntity = metadataModel.get_by_id(uri)
            if metadataEntity:
                metadata = self.getRequest('metadata')
                if metadata and metadata != '0':
                    self.setResponse({'metadata':{
                        'uri':metadataEntity.uri,
                        'type':metadataEntity.type,
                        'size':metadataEntity.size,
                        'uid':metadataEntity.uid,
                        'gid':metadataEntity.gid,
                        'mode':metadataEntity.mode,
                        'ctime':metadataEntity.ctime,
                        'mtime':metadataEntity.mtime,
                        'atime':metadataEntity.atime
                    }})
                elif self.isDataReadable(metadataEntity):
                    dataModel = DataModel()
                    dataEntity = dataModel.get_by_id(uri)
                    if dataEntity:
                        metadataEntity.atime = self.getCurrentTime()
                        metadataEntity.put()
                        self.setResponse(dataEntity.data, 200, metadataEntity.type)
                    else:
                        self.setResponse({'message':'Lost the data'}, 500)
                else:
                    self.setResponse({'message':'Permission denied'}, 403)
            else:
                self.setResponse({'message':'Not found'}, 404)
        elif self.isParentPath(uri):
            metadataModel = MetadataModel()
            metadataEntities = metadataModel.getEntitiesByUri(uri, self.getRequest('sort'))
            if metadataEntities:
                contents = []
                for metadataEntity in metadataEntities:
                    contents.append({
                        'uri':metadataEntity.uri,
                        'type':metadataEntity.type,
                        'size':metadataEntity.size,
                        'uid':metadataEntity.uid,
                        'gid':metadataEntity.gid,
                        'mode':metadataEntity.mode,
                        'ctime':metadataEntity.ctime,
                        'mtime':metadataEntity.mtime,
                        'atime':metadataEntity.atime
                    })
                self.setResponse({'metadata':contents})
            else:
                self.setResponse({'message':'Not found'}, 404)
        else:
            self.setResponse({'message':'Bad request'}, 400)

    def putAction(self, uri=None):
        # Requires:
        # data={multipart form data}
        if self.isResourcePath(uri):
            data = self.getRequest('data', False)
            dataInfo = self.getRequestInfo('data')
            if data and dataInfo:
                convertedData = None
                if dataInfo['isFile']:
                    convertedData = str(data)
                else:
                    convertedData = data.encode('utf-8')

                type = dataInfo['type']
                if not type:
                    type = self.guessMimetypeFromPath(uri)
                    if not type:
                        type = 'application/octet-stream'

                metadataModel = MetadataModel()
                metadataEntity = metadataModel.get_by_id(uri)
                if metadataEntity:
                    if self.isDataWritable(metadataEntity):
                        dataEntity = DataModel(
                            id = uri,
                            data = convertedData
                        )
                        dataEntity.put()

                        metadataEntity.type = type
                        metadataEntity.size = dataInfo['size']
                        metadataEntity.mtime = self.getCurrentTime()
                        metadataEntity.put()

                        self.setResponse({
                            'message':'Updated',
                            'metadata':{
                                'uri':metadataEntity.uri,
                                'type':metadataEntity.type,
                                'size':metadataEntity.size,
                                'uid':metadataEntity.uid,
                                'gid':metadataEntity.gid,
                                'mode':metadataEntity.mode,
                                'ctime':metadataEntity.ctime,
                                'mtime':metadataEntity.mtime,
                                'atime':metadataEntity.atime
                            }
                        })
                    else:
                        self.setResponse({'message':'Permission denied'}, 403)
                else:
                    dataEntity = DataModel(
                        id = uri,
                        data = convertedData
                    )
                    dataEntity.put()

                    ctime = self.getCurrentTime()
                    metadataEntity = MetadataModel(
                        id = uri,
                        uri = uri,
                        type = type,
                        size = dataInfo['size'],
                        uid = self.authUser.uid,
                        gid = self.authUser.uid,
                        mode = '0600',
                        ctime = ctime,
                        mtime = ctime,
                        atime = ctime
                    )
                    metadataEntity.put()

                    self.setResponse({
                        'message':'Created',
                        'metadata':{
                            'uri':metadataEntity.uri,
                            'type':metadataEntity.type,
                            'size':metadataEntity.size,
                            'uid':metadataEntity.uid,
                            'gid':metadataEntity.gid,
                            'mode':metadataEntity.mode,
                            'ctime':metadataEntity.ctime,
                            'mtime':metadataEntity.mtime,
                            'atime':metadataEntity.atime
                        }
                    }, 201)
            else:
                self.setResponse({'message':'Parameter "data" must be set'}, 400)
        else:
            self.setResponse({'message':'Bad request'}, 400)

    def deleteAction(self, uri=None):
        if self.isResourcePath(uri):
            metadataModel = MetadataModel()
            metadataEntity = metadataModel.get_by_id(uri)
            if metadataEntity:
                if self.isDataWritable(metadataEntity):
                    dataModel = DataModel()
                    dataEntity = dataModel.get_by_id(uri)
                    dataEntity.key.delete()

                    metadataEntity.key.delete()

                    self.setResponse({'message':'Deleted'})
                else:
                    self.setResponse({'message':'Permission denied'}, 403)
            else:
                self.setResponse({'message':'Not found'}, 404)
        else:
            self.setResponse({'message':'Bad request'}, 400)

    def isDataReadable(self, metadataEntity):
        uid = self.authUser.uid
        gids = self.authUser.gids.split(',')
        if (('0' in gids)
            or (metadataEntity.uid == uid and int(metadataEntity.mode[1]) >= 4)
            or (metadataEntity.gid in gids and int(metadataEntity.mode[2]) >= 4)
            or (int(metadataEntity.mode[3]) >= 4)):
            return True
        return False

    def isDataWritable(self, metadataEntity):
        uid = self.authUser.uid
        gids = self.authUser.gids.split(',')
        if (('0' in gids)
            or (metadataEntity.uid == uid and int(metadataEntity.mode[1]) >= 6)
            or (metadataEntity.gid in gids and int(metadataEntity.mode[2]) >= 6)
            or (int(metadataEntity.mode[3]) >= 6)):
            return True
        return False
