FROM node:26-alpine

WORKDIR /assets

COPY package.json package-lock.json ./

RUN \
  npm ci && \
  npm cache clean --force && \
  chown -R node:node /assets

USER node

EXPOSE 5173

CMD ["npm", "run", "dev"]
