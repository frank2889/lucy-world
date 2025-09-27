#!/bin/bash

# Update script for Lucy World Search
# Use this to update the application after code changes

set -e

APP_DIR="/var/www/lucy-world-search"
BACKUP_DIR="/var/backups/lucy-world-search"

echo "🔄 Lucy World Search - Update Starting..."

# Create backup
echo "💾 Creating backup..."
sudo mkdir -p $BACKUP_DIR
sudo cp -r $APP_DIR $BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S)

# Pull latest code (if using git)
cd $APP_DIR
echo "📥 Pulling latest code..."
# git pull origin main  # Uncomment if using git

# Copy new files (if deploying manually)
echo "📋 Copying updated files..."
# Assuming you upload files to a temp directory first
# cp -r /tmp/lucy-world-search-update/* $APP_DIR/

# Activate virtual environment
source venv/bin/activate

# Update dependencies
echo "📚 Updating dependencies..."
pip install -r requirements-prod.txt

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data $APP_DIR

# Restart application
echo "🔄 Restarting application..."
sudo systemctl restart lucy-world-search

# Check status
echo "📊 Checking status..."
sleep 3
sudo systemctl status lucy-world-search --no-pager -l

echo "✅ Update completed successfully!"