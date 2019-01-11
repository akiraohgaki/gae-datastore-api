import time
import uuid
import mimetypes
import json
import cgi
import logging

import webapp2
from google.appengine.api import mail

from application.models.UsersModel import UsersModel
from application.models.AccessTokensModel import AccessTokensModel

class BaseHandler(webapp2.RequestHandler):

    authUser = None

    isAdmin = False

    isAuthRequired = False

    '''
    Method overriding
    '''
    def __init__(self, request, response):
        self.initialize(request, response)

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        status = 500
        message = 'An error occurred'
        if isinstance(exception, webapp2.HTTPException):
            status = exception.code
        if debug:
            message = exception.message
        self.setResponse({'message':message}, status)

    '''
    Default actions of request handling
    '''
    def options(self, uri=None):
        self.setResponse({'message':'Allow: OPTIONS, HEAD, GET, POST, PUT, DELETE'})

    def trace(self, uri=None):
        self.setResponse({'message':'Method not allowed'}, 405)

    def head(self, uri=None):
        # Sets raw size of content body to "Content-Length" header
        # But it size will difference when GET response with gzip encoded
        self.get(uri)
        contentLength = self.response.headers.get('Content-Length')
        self.response.clear()
        self.response.headers['Content-Length'] = contentLength

    def post(self, uri=None):
        # Switch request method if client sent parameter "method"
        # or header "X-HTTP-Method-Override" by POST method
        # method=GET|PUT|DELETE
        # X-HTTP-Method-Override: GET|PUT|DELETE
        method = self.getRequest('method')
        if not method:
            method = self.getRequestHeader('X-HTTP-Method-Override')

        if method:
            method = method.upper()
            if method == 'GET':
                self.get(uri)
            elif method == 'PUT':
                self.put(uri)
            elif method == 'DELETE':
                self.delete(uri)
            else:
                self.setResponse({'message':'Parameter "method" value or header "X-HTTP-Method-Override" value must be GET,PUT or DELETE'}, 400)
        elif self.isAuthRequired and not self.authenticateUser():
            self.setResponse({'message':'Unauthorized'}, 401)
        else:
            self.postAction(uri)

    def get(self, uri=None):
        if self.isAuthRequired and not self.authenticateUser():
            self.setResponse({'message':'Unauthorized'}, 401)
        else:
            self.getAction(uri)

    def put(self, uri=None):
        if self.isAuthRequired and not self.authenticateUser():
            self.setResponse({'message':'Unauthorized'}, 401)
        else:
            self.putAction(uri)

    def delete(self, uri=None):
        if self.isAuthRequired and not self.authenticateUser():
            self.setResponse({'message':'Unauthorized'}, 401)
        else:
            self.deleteAction(uri)

    def postAction(self, uri=None):
        self.setResponse({'message':'Not implemented'}, 501)

    def getAction(self, uri=None):
        self.setResponse({'message':'Not implemented'}, 501)

    def putAction(self, uri=None):
        self.setResponse({'message':'Not implemented'}, 501)

    def deleteAction(self, uri=None):
        self.setResponse({'message':'Not implemented'}, 501)

    '''
    Base class methods
    '''
    def getRequest(self, key, filter=True):
        value = self.request.get(key)
        if value and filter:
            value = value.strip()
            value = value.replace("\r\n", "\n")
            value = value.replace("\r", "\n")
            value = value.replace("\0", '')
        return value

    def getRequestHeader(self, key, filter=True):
        value = self.request.headers.get(key)
        if value and filter:
            value = value.strip()
            value = value.replace("\0", '')
        return value

    def getRequestInfo(self, key):
        if key in self.request.params:
            field = self.request.params[key] # value or FieldStorage
            info = {
                'name':key,
                'isFile':False,
                'value':None,
                'file':None,
                'filename':None,
                'type':None,
                'size':0
            }
            if isinstance(field, cgi.FieldStorage):
                if field.file:
                    info['isFile'] = True
                    info['file'] = field.file
                    info['filename'] = field.filename
                    info['type'] = field.type
                    field.file.seek(0, 2)
                    info['size'] = field.file.tell()
                    field.file.seek(0)
                else:
                    info['value'] = field.value
                    info['size'] = len(field.value)
            else:
                info['value'] = field
                info['size'] = len(field)
            return info
        return None

    def setResponse(self, content, status=200, type=None):
        if not type:
            # Make JSON content as default
            type = 'application/json'
            data = {'status':'unknown'}
            if 200 <= status < 300:
                data['status'] = 'success'
            elif 400 <= status < 500:
                data['status'] = 'error'
                if status == 400:
                    self.response.headers['WWW-Authenticate'] = 'Bearer realm="' + self.request.host + '", error="invalid_request"'
                elif status == 401:
                    self.response.headers['WWW-Authenticate'] = 'Bearer realm="' + self.request.host + '", error="invalid_token"'
                elif status == 403:
                    self.response.headers['WWW-Authenticate'] = 'Bearer realm="' + self.request.host + '", error="insufficient_scope"'
            elif 500 <= status < 600:
                data['status'] = 'failure'
            data.update(content)
            content = json.dumps(data)

            # Make JSONP content if parameter 'callback' has set
            callback = self.getRequest('callback')
            if callback:
                type = 'text/javascript'
                content = cgi.escape(callback, True) + '(' + content + ')'

            # Always OK status if parameter 'ignore_status_code' has set
            # ignore_status_code=1|0
            ignore = self.getRequest('ignore_status_code')
            if ignore and ignore != '0':
                status = 200

        self.response.status = status
        self.response.content_type = str(type)
        self.response.content_type_params = {'charset':'UTF-8'}

        origin = self.getRequestHeader('Origin')
        if origin:
            self.response.headers['Access-Control-Allow-Origin'] = origin
            self.response.headers['Access-Control-Allow-Credentials'] = 'true'
            self.response.headers['Access-Control-Max-Age'] = '1728000'

        if self.getRequestHeader('Access-Control-Request-Method'):
            self.response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'

        if self.getRequestHeader('Access-Control-Request-Headers'):
            self.response.headers['Access-Control-Allow-Headers'] = 'Origin, Authorization, Content-Type, Accept, X-HTTP-Method-Override, X-Requested-With, X-Csrftoken'
            self.response.headers['Access-Control-Expose-Headers'] = 'Authorization, Content-Type, Accept'

        self.response.write(str(content))

    def authenticateUser(self):
        # User authentication by header 'Authorization: Bearer'
        # or parameter 'access_token'
        token = None
        bearerToken = self.getRequestHeader('Authorization')
        accessToken = self.getRequest('access_token')
        if bearerToken and bearerToken.lower().startswith('bearer '):
            token = bearerToken[7:]
        elif accessToken:
            token = accessToken

        if token:
            accessTokensModel = AccessTokensModel()
            accessTokenEntity = accessTokensModel.getActiveEntityById(token)
            if accessTokenEntity:
                usersModel = UsersModel()
                userEntity = usersModel.getActiveEntityById(accessTokenEntity.uid)
                if userEntity:
                    self.authUser = userEntity
                    if '0' in userEntity.gids.split(','):
                        self.isAdmin = True
                    return True
        return False

    def generateUuid(self):
        return str(uuid.uuid4())

    def getCurrentTime(self):
        return int(time.time())

    def getAccessTokenExpires(self):
        return self.getCurrentTime() + (86400 * self.app.config['access_token_expires'])

    def isParentPath(self, path):
        if path and path.endswith('/'):
            return True
        return False

    def isResourcePath(self, path):
        if path and not path.endswith('/'):
            return True
        return False

    def guessMimetypeFromPath(self, path):
        type, encoding = mimetypes.guess_type(path)
        return type

    def sendEmailNotification(self, subject, body):
        notification = mail.EmailMessage(
            sender=str(self.app.config['email']),
            to=str(self.app.config['email']),
            subject=subject,
            body=body
        )
        notification.send()
