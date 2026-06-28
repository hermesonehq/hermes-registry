#!/bin/bash

ENV=${1:-$ENV}
PROJECT_ID=${2:-$PROJECT_ID}
REGION=${3:-$REGION}
USER=${4:-$USER}

if [[ -z "${PROJECT_ID}" ]]; then
    echo "Error: PROJECT_ID is not set (neither as an argument nor as an environment variable)."
    exit 1
fi

if [[ -z "${USER}" ]]; then
    echo "Error: USER is not set (neither as an argument nor as an environment variable)."
    exit 1
fi

if [[ -z "${ENV}" ]]; then
    ENV="prod"
fi

if [[ -z "${REGION}" ]]; then
    echo "Error: REGION is not set (neither as an argument nor as an environment variable)."
    exit 1
fi

ENDPOINT="https://${REGION}-${ENV}-aiplatform.sandbox.googleapis.com"

echo "PROJECT_ID: ${PROJECT_ID}"
echo "USER: ${USER}"
echo "Env: ${ENV}"
echo "Region: ${REGION}"
echo "Endpoint: ${ENDPOINT}"

if ! gcloud config configurations describe "${ENV}-cdmodel" > /dev/null 2>&1; then
  gcloud config configurations create "${ENV}-cdmodel"
  gcloud config set core/project "${PROJECT_ID}"
  gcloud config set compute/region "${REGION}"
  gcloud config set account "${USER}"@google.com
  gcloud config set api_endpoint_overrides/aiplatform "${ENDPOINT}"
fi

gcloud config configurations activate ${ENV}-cdmodel

# gcloud config configurations delete prod-cdmodel
