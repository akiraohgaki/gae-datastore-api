#!/bin/sh

# Create application config
echo "${APPLICATION_CONFIG}" > 'default/application/configs/application.json'

# Install Google Cloud SDK
CLOUDSDK_PACKAGE='google-cloud-sdk-185.0.0-linux-x86_64.tar.gz'
curl -fsSL -o "${HOME}/${CLOUDSDK_PACKAGE}" "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/${CLOUDSDK_PACKAGE}"
tar -xzf "${HOME}/${CLOUDSDK_PACKAGE}" -C "${HOME}"
export PATH="${PATH}:${HOME}/google-cloud-sdk/bin"

# Install SDK components
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
gcloud components install app-engine-python

# Activate service account
echo "${GOOGLE_CLIENT_SECRET}" > "${HOME}/client-secret.json"
gcloud auth activate-service-account --key-file "${HOME}/client-secret.json"

# Deploy
gcloud app deploy default/app.yaml --promote --quiet --verbosity=error
gcloud app deploy dispatch.yaml --quiet --verbosity=error
