# NGINX Dockerfile
This image uses the latest NGINX docker image, and then adds the following changes:

- [nginx.conf](./nginx.conf): changed to include `include /etc/nginx/sites-enabled/*;` in http.
- [hostfile](./hostfile): changed to include `127.0.0.1       localhost *.localhost` to allow for localhost subdomains.
- [proxy_params](./proxy_params): included to support default proxy params.
- [sites-enabled/datastore](./sites-enabled/datastore): enables the django administration panel, and connects incoming requests to solr. (needs elaboration)
- [sites-enabled/flower](./sites-enabled/flower): enables the flower interface.
- [sites-enabled/iati.cloud-redirect](./sites-enabled/iati.cloud-redirect): enables redirects from the original iati.cloud domain to the current domain.
