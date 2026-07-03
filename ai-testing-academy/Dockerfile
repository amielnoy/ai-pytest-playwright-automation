# Static web server for the AI Testing Academy site.
#
# Build:  docker build -t ai-testing-academy ai-testing-academy
# Run:    docker run --rm -p 8080:80 ai-testing-academy      →  http://localhost:8080
# With the agents' API keys auto-loaded from your .env:
#         docker run --rm -p 8080:80 \
#           -v "$PWD/.env:/usr/share/nginx/html/.env:ro" ai-testing-academy
FROM nginx:1.27-alpine

# Copy the academy site to the web root. The English page is the default index;
# the Hebrew page and the language switcher are reachable from it.
COPY . /usr/share/nginx/html/

# Minimal server config: serve static files, default to the English landing page.
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index ai-testing-academy.html;\n\
    location / { try_files $uri $uri/ =404; }\n\
    location ~* \\.(svg|png|jpe?g|gif|mp4|webm|css|js|woff2?)$ { expires 7d; access_log off; }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
