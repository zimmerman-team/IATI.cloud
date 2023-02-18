FROM nginx:latest

ARG IC_DOMAIN
ARG SOLR_AUTH_ENCODED

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./hostfile /etc/hosts
COPY ./proxy_params /etc/nginx/proxy_params

# Flower
COPY ./sites-enabled/flower  /etc/nginx/sites-enabled/flower
RUN sed -i "s|IC_DOMAIN|${IC_DOMAIN}|g" /etc/nginx/sites-enabled/flower

# Django
COPY ./sites-enabled/datastore  /etc/nginx/sites-enabled/datastore
RUN sed -i "s|IC_DOMAIN|${IC_DOMAIN}|g" /etc/nginx/sites-enabled/datastore
# RUN sed -i "s|http://solr:8983|http://${SOLR_ADMIN_USERNAME}:${SOLR_ADMIN_PASSWORD}@solr:8983|g" /etc/nginx/sites-enabled/datastore
RUN sed -i "s|SOLR_AUTH_ENCODED|${SOLR_AUTH_ENCODED}|g" /etc/nginx/sites-enabled/datastore

# Redirect -- disabled by default, feel free to enable in production
# COPY ./sites-enabled/iati.cloud-redirect  /etc/nginx/sites-enabled/iati.cloud-redirect
# RUN sed -i "s|IC_DOMAIN|${IC_DOMAIN}|g" /etc/nginx/sites-enabled/iati.cloud-redirect
