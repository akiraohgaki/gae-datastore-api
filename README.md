# gae-datastore-api

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

API app for Cloud Datastore.

Copyright: 2017, Akira Ohgaki

License: BSD-2-Clause

## Deployment

On Google Cloud Platform, enable API.

* App Engine Admin API
* Google Cloud Storage
* Google Cloud Storage JSON API

And create a service account and add a role.

* App Engine Admin
* Cloud Storage object Admin

OR

* App Engine deployer
* App Engine service admin
* Cloud Storage object readable
* Cloud Storage object writeable

Then set environment variables in localhost or CI pipelines.

* CLOUDSDK_CORE_PROJECT = Project ID
* GOOGLE_CLIENT_SECRET = Secret key (JSON) of service account
* APPLICATION_CONFIG = Application config data (JSON) of application.json

And execute "deploy.sh".

```
./deploy.sh
```

## Initializing application

On App Engine settings, add your Gmail to authorized sender list,
then call "/datastore/admin/init"

```
POST /datastore/admin/init
```
