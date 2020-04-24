FROM docker.io/debian:buster-slim


# Install base system dependencies
RUN apt update
# https://stackoverflow.com/questions/58160597/docker-fails-with-sub-process-usr-bin-dpkg-returned-an-error-code-1
RUN mkdir -p /usr/share/man/man1 
RUN apt install -y --no-install-recommends uwsgi uwsgi-plugin-python3 python3 python3-setuptools pipenv gcc gettext libldap2-dev libsasl2-dev libgpgme-dev python3-dev libgraphviz-dev graphviz libmagic-dev libjs-mathjax libpcre3 libpcre3-dev make yui-compressor
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 99


# add Pipfile seperate from other sources to take advantage of docker build caching
ADD Pipfile /app/src/Pipfile
ADD Pipfile.lock /app/src/Pipfile.lock
WORKDIR /app/src

RUN pipenv install --system --deploy --ignore-pipfile
RUN pip3 install uwsgi sentry-sdk

# add remaining sources
ADD . /app/src

# Link up configs to appropriate locations
RUN mkdir -p /app/config; \
    cp /app/src/docker/uwsgi.ini /app/config/uwsgi.ini; \
    cp /app/src/mafiasi/settings.py.example /app/config/settings.py; \
    ln -sf /app/config/settings.py /app/src/mafiasi/settings.py
# compile staticfiles and messages
RUN make all

# Configure Image Metadata
ENTRYPOINT ["/app/src/docker/entrypoint.sh"]
ENV LANG=en_US.UTF-8
VOLUME /app/static      # django staticfiles get copied here. can be used to serve them via external webserver.
VOLUME /app/media       # user uploaded content (like gprot) get sput here
EXPOSE 3003     # uwsgi
EXPOSE 8000     # http

