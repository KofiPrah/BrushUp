#!/bin/bash

# Navigate to the frontend directory
cd frontend/artcritique-frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Start the development server
echo "Starting React development server..."
npm run dev