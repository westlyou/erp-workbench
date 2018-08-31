# Dockerfile
#FROM debian:stretch
FROM ubuntu:artful

# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - ;sh -c 'echo "deb [trusted=yes] http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list'
#RUN echo "deb [trusted=yes] http://apt.postgresql.org/pub/repos/apt/ artful-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && \
    apt-get install postgresql-client-10 vim python -y --allow-unauthenticated


ENTRYPOINT ["/usr/bin/python", "/mnt/sites/dumper/dumper.py"]
 
