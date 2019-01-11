from application.handlers.BaseHandler import BaseHandler

from application.models.UsersModel import UsersModel
from application.models.AccessTokensModel import AccessTokensModel

class UsersHandler(BaseHandler):

    '''
    /users/me is a shorthand of /users/username
    '''

    isAuthRequired = True

    def getAction(self, uri=None):
        if uri == 'me':
            uri = self.authUser.username

        if self.isResourcePath(uri):
            userEntity = None
            if uri == self.authUser.username:
                userEntity = self.authUser
            else:
                usersModel = UsersModel()
                userEntity = usersModel.getActiveEntityByUsername(uri)

            if userEntity:
                self.setResponse({'user':{
                    'uid':userEntity.uid,
                    'gids':userEntity.gids,
                    'username':userEntity.username
                }})
            else:
                self.setResponse({'message':'Not found'}, 404)
        elif not uri:
            usersModel = UsersModel()
            userEntities = usersModel.getActiveEntities()
            if userEntities:
                contents = []
                for userEntity in userEntities:
                    contents.append({
                        'uid':userEntity.uid,
                        'gids':userEntity.gids,
                        'username':userEntity.username
                    })
                self.setResponse({'users':contents})
            else:
                self.setResponse({'message':'Not found'}, 404)
        else:
            self.setResponse({'message':'Bad request'}, 400)

    def putAction(self, uri=None):
        if uri == 'me':
            uri = self.authUser.username

        if self.isResourcePath(uri):
            userEntity = None
            if uri == self.authUser.username:
                userEntity = self.authUser
            elif self.isAdmin:
                usersModel = UsersModel()
                userEntity = usersModel.getActiveEntityByUsername(uri)

            if userEntity:
                # Nothing to do, just put for now
                userEntity.put()

                self.setResponse({
                    'message':'Updated',
                    'user':{
                        'uid':userEntity.uid,
                        'gids':userEntity.gids,
                        'username':userEntity.username
                    }
                })
            elif self.isAdmin:
                uid = self.generateUuid()
                userEntity = UsersModel(
                    id = uid,
                    uid = uid,
                    gids = uid,
                    username = uri,
                    active = 1
                )
                userEntity.put()

                # Set access token
                token = self.generateUuid()
                accessTokenEntity = AccessTokensModel(
                    id = token,
                    token = token,
                    uid = uid,
                    expires = self.getAccessTokenExpires()
                )
                accessTokenEntity.put()

                self.sendEmailNotification('User created', 'Access token for ' + uri + ': ' + token)

                self.setResponse({
                    'message':'Created',
                    'user':{
                        'uid':userEntity.uid,
                        'gids':userEntity.gids,
                        'username':userEntity.username
                    }
                }, 201)
            else:
                self.setResponse({'message':'Permission denied'}, 403)
        else:
            self.setResponse({'message':'Bad request'}, 400)

    def deleteAction(self, uri=None):
        if uri == 'me':
            uri = self.authUser.username

        if self.isResourcePath(uri):
            userEntity = None
            if uri == self.authUser.username:
                userEntity = self.authUser
            elif self.isAdmin:
                usersModel = UsersModel()
                userEntity = usersModel.getActiveEntityByUsername(uri)

            if userEntity:
                userEntity.active = 0
                userEntity.put()
                # TODO: Makes a garbage collection
                self.setResponse({'message':'The user deactivated'})
            elif self.isAdmin:
                self.setResponse({'message':'Not found'}, 404)
            else:
                self.setResponse({'message':'Permission denied'}, 403)
        else:
            self.setResponse({'message':'Bad request'}, 400)
