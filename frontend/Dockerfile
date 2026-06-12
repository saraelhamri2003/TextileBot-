FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# Start dev server pointing host flag
CMD ["npm", "run", "dev", "--", "--host"]
