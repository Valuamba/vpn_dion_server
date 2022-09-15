FROM python:bullseye

# Install dependencies
RUN apt-get update && apt-get install -y systemd nginx htop  \
    netdata fail2ban wireguard iptables  \
    vim gunicorn uvicorn  \
    python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
    #resolvconf qrencode
#    wireguard iptables resolvconf qrencode

#
#RUN apt-get install -y python3.6
#CMD alias python=/usr/bin/python3.6

WORKDIR /src
#COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY ./requirements.txt /src/requirements.txt

CMD ["/etc/init.d/nginx", "restart"]

RUN pip install -r requirements.txt
#RUN wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh && sh /tmp/netdata-kickstart.sh
COPY . .

#gunicorn -b 0.0.0.0:5000 wsgi:app
#/usr/sbin/nginx -g "daemon off;"
CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "wsgi:app"]
#CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
#CMD [ "bash", "/src/scripts/install-wireguard.sh"]

