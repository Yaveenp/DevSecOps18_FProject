# Use Node.js alpine image for smaller size
FROM --platform=$BUILDPLATFORM node:18-alpine

# Add build platform args
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Install a simple static server
RUN npm install -g serve

# Expose the port your app will run on
EXPOSE 3001

# Start the production server
CMD ["serve", "-s", "build", "-l", "3001"]
