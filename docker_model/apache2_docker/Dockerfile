FROM python:3.6
RUN apt-get update && apt-get -y upgrade\
    && apt-get -y install apache2 libapache2-mod-wsgi-py3 \
    && pip3.6 install Django -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && rm /etc/apache2/sites-enabled/000-default.conf \
    && ln -s /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/000-default.conf
COPY ./sources.list /etc/apt/sources.list
COPY apache/ /etc/apache2/
RUN cd /var/www
RUN django-admin.py startproject neutrino
EXPOSE 80
CMD /etc/init.d/apache2 start
