from application.handlers.BaseHandler import BaseHandler

from application.models.UsersModel import UsersModel
from application.models.AccessTokensModel import AccessTokensModel

class AdminHandler(BaseHandler):

    def postAction(self, uri=None):
        if uri == 'init':
            # Create root user
            uid = '0'
            usersModel = UsersModel()
            userEntity = usersModel.get_by_id(uid)
            if not userEntity:
                userEntity = UsersModel(
                    id = uid,
                    uid = uid,
                    gids = uid,
                    username = 'root',
                    active = 1
                )
                userEntity.put()

                # Set access token for root user
                token = self.generateUuid()
                accessTokenEntity = AccessTokensModel(
                    id = token,
                    token = token,
                    uid = uid,
                    expires = self.getAccessTokenExpires()
                )
                accessTokenEntity.put()

                self.sendEmailNotification('User created', 'Access token for root: ' + token)

                self.setResponse({'message':'Initialized'})
                return
        elif uri == 'add_access_token':
            # Parameters:
            # username={username}
            username = self.getRequest('username')
            if username:
                usersModel = UsersModel()
                userEntity = usersModel.getActiveEntityByUsername(username)
                if userEntity:
                    token = self.generateUuid()
                    accessTokenEntity = AccessTokensModel(
                        id = token,
                        token = token,
                        uid = userEntity.uid,
                        expires = self.getAccessTokenExpires()
                    )
                    accessTokenEntity.put()

                    self.sendEmailNotification('Access token added', 'Access token for ' + username + ': ' + token)

                    self.setResponse({'message':'Added'})
                    return

        self.setResponse({'message':'Bad request'}, 400)
