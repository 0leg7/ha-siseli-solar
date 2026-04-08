ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    nodejs \
    npm \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    jq

WORKDIR /app
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

COPY package.json /app/
RUN npm install --production

COPY run.sh /app/
COPY get_token.js /app/
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
