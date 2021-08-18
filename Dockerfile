FROM docker.io/debian:buster-slim

# https://stackoverflow.com/questions/58160597/docker-fails-with-sub-process-usr-bin-dpkg-returned-an-er
RUN mkdir -p /usr/share/man/man1

# Install base system dependencies
RUN apt update && \
    apt install -y --no-install-recommends uwsgi uwsgi-plugin-python3 python3 python3-pip \
    python3-setuptools pipenv gcc gettext libldap-2.4-2 libldap2-dev libsasl2-2 libsasl2-dev \
    libgpgme11 libgpgme-dev python3-dev libgraphviz-dev graphviz libmagic-dev libjs-mathjax make \
    yui-compressor nginx supervisor && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 99

# add Pipfile separate from other sources to take advantage of build caching
ADD Pipfile /app/src/Pipfile
ADD Pipfile.lock /app/src/Pipfile.lock
WORKDIR /app/src
RUN pip3 install -U pip && \
    pipenv install --system --deploy --ignore-pipfile && \
    pip3 install sentry-sdk typing-extensions

# add remaining sources
ADD . /app/src

# Put configs in appropriate locations
RUN cp docker/nginx.conf /etc/nginx/sites-enabled/default && \
    cp docker/uwsgi.ini /etc/uwsgi/mafiasi-dashboard.ini && \
    cp docker/supervisor.conf /etc/supervisor/conf.d/app.conf && \
    mkdir /app/config && \
    cp mafiasi/settings.py.example /app/config/settings.py && \
    ln -sf /app/config/settings.py /app/src/mafiasi/settings.py && \
    touch /app/config/jabber_cert_fingerprint && \
    touch /app/config/mumble_cert_fingerprint

# compile staticfiles and messages
RUN make all && \
    ./manage.py collectstatic --no-input && \
    mkdir -p /app/static/mathjax && \
    cp -rT /usr/share/javascript/mathjax /app/static/mathjax

# Configure Image Metadata
ENTRYPOINT ["/app/src/docker/entrypoint.sh"]
CMD supervisord -n -c /etc/supervisor/supervisord.conf -u root
ENV LANG=en_US.UTF-8
ENV HOME=/app
# user uploaded content (like gprot) get put here
VOLUME /app/media
# pks keyring
VOLUME /app/.gnupg
# http
EXPOSE 8000
