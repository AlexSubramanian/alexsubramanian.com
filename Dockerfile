FROM hugomods/hugo:exts AS builder
COPY . /src
WORKDIR /src
RUN hugo --minify

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /src/public /srv/site
