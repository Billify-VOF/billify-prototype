FROM nginx:stable-alpine3.17-slim
RUN apk update && apk upgrade busybox ssl_client
COPY ./nginx/infra.conf /etc/nginx/conf.d
# COPY ./somthing/static/ /static/
RUN rm -rf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
EXPOSE 80
EXPOSE 443
