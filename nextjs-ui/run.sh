#!/bin/bash
npm i

# Run build and check for success
if npm run build; then
    echo "✅ Build succeeded. Restarting PM2 services..."
    pm2 delete all
    pm2 start "npm start -- -p 4173" --name "rerite-frontend-0"
    pm2 start "npm start -- -p 4174" --name "rerite-frontend-1"
else
    echo "❌ Build failed! Keeping the previous version running."
    exit 1  # Exit without stopping the running version
fi