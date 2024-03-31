# Define function directory
ARG FUNCTION_DIR="/function"

FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy as build-image

# Install aws-lambda-cpp build dependencies
RUN apt-get update
RUN apt-get install -y g++
RUN apt-get install -y make
RUN apt-get install -y cmake
RUN apt-get install -y unzip
RUN apt-get install -y libcurl4-openssl-dev

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Copy function code
COPY app/* ${FUNCTION_DIR}

# Install the runtime interface client
RUN python -m pip install --upgrade pip
RUN python -m pip install --target ${FUNCTION_DIR} playwright awslambdaric

# Install the runtime (you need)
RUN python -m pip install --target ${FUNCTION_DIR} boto3 pandas

# Multi-stage build: grab a fresh copy of the base image
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Include global arg in this stage of the build
ARG FUNCTION_DIR

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Copy in the build image dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}

ENTRYPOINT [ "/usr/bin/python", "-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]
