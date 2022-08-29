FROM nginx:latest


COPY nginx.conf /etc/nginx/conf.d


EXPOSE 8000

STOPSIGNAL SIGTERM

CMD ["nginx", "-g", "daemon off;"]