# medoru_api

The API for https://medoru.net.

## Run locally

```bash
./bin/run.sh

## Setup a server

### Install system packages

```
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv nginx
```

### Create app directories

Let's use an user called `medoru`, so:

```
sudo mkdir -p /var/opt/medoru_api
sudo mkdir -p /etc/medoru_api

sudo chown -R medoru:medoru /var/opt/medoru_api
sudo chown -R root:medoru /etc/medoru_api
sudo chmod 750 /etc/medoru_api
```

### Create production env file

```
sudo vim /etc/medoru_api/medoru_api.env
```

Put:

```
APP_NAME=medoru_api
APP_VERSION=0.1.0
APP_HOST=127.0.0.1
APP_PORT=5000
DEBUG=false
DATABASE_URL=PUT_THE_PRODUCTION_DATABASE_URL_HERE
```

and

```
sudo chown root:medoru /etc/medoru_api/medoru_api.env
sudo chmod 640 /etc/medoru_api/medoru_api.env
```

### Create nginx vhost

```
sudo vim /etc/nginx/conf.d/api.medoru.net.conf
```

with

```
server {
    listen 80;
    server_name api.medoru.net;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then test and reload:

```
sudo nginx -t
sudo systemctl reload nginx
```

### Setup and update

It is done with:

```
cd deployment

ansible-playbook -i inventory/production update.yml -K
```
