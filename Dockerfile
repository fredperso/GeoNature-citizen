FROM debian:buster-slim

## install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y sudo vim nano locales unzip && \
    localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8 && \
    apt-get clean

## set LANG env
ENV LANG fr_FR.utf8

#RUN addgroup --gid 1001 appuser && adduser --disabled-password --gecos 'AppUser' --uid 1001 --group --shell /bin/bash appuser
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser -m -d /home/appuser appuser
#RUN adduser --disabled-password --gecos 'AppUser' --uid 1001 --group --shell /bin/bash appuser
RUN usermod -aG sudo appuser 
RUN echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

COPY . /home/appuser/citizen
RUN chown -R appuser:appuser /home/appuser

USER appuser

WORKDIR /home/appuser/citizen

VOLUME /var/lib/postgresql
VOLUME /etc/postgresql
VOLUME /etc/apache2 

EXPOSE 80
EXPOSE 5432
