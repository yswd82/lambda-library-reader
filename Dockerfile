# Define function directory
ARG FUNCTION_DIR="/function"

# Repository for playwright python image 
# https://mcr.microsoft.com/en-us/artifact/mar/playwright/python
FROM mcr.microsoft.com/playwright/python:v1.63.0-amd64 AS build-image

# Install aws-lambda-cpp build dependencies
RUN apt-get update
RUN apt-get install -y make
RUN apt-get install -y unzip
RUN apt-get install -y libcurl4-openssl-dev
# RUN apt-get update && apt-get install -y python-pip

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY src/* ${FUNCTION_DIR}

# Install the runtime interface client
# RUN python3 -m pip install --upgrade pip --break-system-packages
RUN python -m pip install --target ${FUNCTION_DIR} playwright==1.63.0 awslambdaric --break-system-packages

# Install the runtime (you need)
RUN python -m pip install --target ${FUNCTION_DIR} boto3 pandas --break-system-packages

# Multi-stage build: grab a fresh copy of the base image
FROM mcr.microsoft.com/playwright/python:v1.63.0-amd64

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]
