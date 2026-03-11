FROM alpine:3.21 AS pdf-converter
RUN apk add --no-cache libreoffice font-carlito font-liberation
COPY content/resume/*.docx /tmp/
RUN libreoffice --headless --convert-to pdf --outdir /tmp/ /tmp/*.docx

FROM hugomods/hugo:exts AS builder
COPY . /src
COPY --from=pdf-converter /tmp/*.pdf /src/static/files/resume.pdf
WORKDIR /src
RUN hugo --minify

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=builder /src/public /srv/site
