FROM docker.io/debian:bullseye-slim as git
RUN apt-get update &&\
    apt-get install -y git ca-certificates  &&\
    git clone https://git.kritzl.dev/kritzl/hvvstuhl.de.git /usr/src/hvvstuhl.de/



FROM docker.io/nginx:mainline
COPY --from=git /usr/src/hvvstuhl.de/ /usr/src/hvvstuhl.de/
RUN rm -rf /usr/share/nginx/html &&\
    ln -sf /usr/src/hvvstuhl.de/ /usr/share/nginx/html
EXPOSE 80/tcp
