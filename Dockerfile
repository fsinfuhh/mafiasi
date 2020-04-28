FROM docker.io/debian:buster-slim


# Install base system dependencies
RUN apt update
# https://stackoverflow.com/questions/58160597/docker-fails-with-sub-process-usr-bin-dpkg-returned-an-error-code-1
RUN mkdir -p /usr/share/man/man1 
RUN apt install -y --no-install-recommends uwsgi uwsgi-plugin-python3 python3 python3-setuptools pipenv gcc gettext \
    libldap2-dev libsasl2-dev libgpgme-dev python3-dev libgraphviz-dev graphviz libmagic-dev libjs-mathjax \
    libpcre3 libpcre3-dev make yui-compressor nginx supervisor
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 99

# add Pipfile seperate from other sources to take advantage of build caching
ADD Pipfile /app/src/Pipfile
ADD Pipfile.lock /app/src/Pipfile.lock
WORKDIR /app/src
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip3 install sentry-sdk

# add remaining sources
ADD . /app/src

# Put configs in appropriate locations
ADD docker/nginx.conf /etc/nginx/sites-enabled/default
ADD docker/uwsgi.ini /etc/uwsgi/mafiasi-dashboard.ini
ADD docker/supervisor.conf /etc/supervisor/conf.d/app.conf
ADD mafiasi/settings.py.example /app/config/settings.py
RUN ln -sf /app/config/settings.py /app/src/mafiasi/settings.py
RUN touch /app/config/jabber_cert_fingerprint
RUN touch /app/config/mumble_cert_fingerprint

# compile staticfiles and messages
RUN make all
RUN ./manage.py collectstatic --no-input

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
