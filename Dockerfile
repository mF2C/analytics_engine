# Base Image for the analytics_engine Docker Deployment

FROM ubuntu:16.04
LABEL maintainer="giuliana.carullo@intel.com"

RUN apt-get update && apt-get install -y git python python-pip python-dev python-pycurl libssl-dev libcurl4-openssl-dev netcat

# Set the working directory to /app
WORKDIR /analytics_engine
COPY ./ /analytics_engine

RUN $WORKDIR
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Set PYTHONPATH as root directory
ENV PYTHONPATH .

#WORKDIR /analytics_engine


RUN python setup.py install
CMD ["analytics_engine", "--run", "rest"]
