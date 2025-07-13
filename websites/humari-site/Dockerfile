FROM node:18-alpine
RUN apk --no-cache add curl

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --silent

EXPOSE 3000
ENV NODE_ENV=production

# 🎯 Build avec cache intelligent + restart-friendly
CMD ["sh", "-c", "npm run build:clean && npm run start"]