FROM node:18-alpine as builder

RUN apk add --no-cache libc6-compat make g++ pixman-dev cairo-dev pango-dev

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci


FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/node_modules/ ./node_modules
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]