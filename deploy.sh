#!/bin/bash

# Lucy World Search Deployment Script voor DigitalOcean
# Dit script installeert en start de applicatie

set -e

echo "🚀 Lucy World Search - Deployment Starting..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and required system packages
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git htop

# Create application directory
APP_DIR="/var/www/lucy-world-search"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files (assuming files are in current directory)
echo "📋 Copying application files..."
cp -r * $APP_DIR/
cd $APP_DIR

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements-prod.txt

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOL
FLASK_ENV=production
FLASK_APP=app.py
PORT=8000
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
EOL

# Create systemd service file
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/lucy-world-search.service > /dev/null << EOL
[Unit]
Description=Lucy World Search Gunicorn App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Set correct permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/lucy-world-search > /dev/null << EOL
server {
    listen 80;
    server_name lucy.world;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Main Lucy World homepage (future)
    location / {
        return 301 /search;
    }
    
    # Keyword Search Tool
    location /search {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # API endpoints
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Favicon
    location /favicon.ico {
        alias $APP_DIR/static/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOL

# Enable site
sudo ln -sf /etc/nginx/sites-available/lucy-world-search /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable lucy-world-search
sudo systemctl start lucy-world-search
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check service status
echo "📊 Checking service status..."
sudo systemctl status lucy-world-search --no-pager -l
sudo systemctl status nginx --no-pager -l

# Install SSL certificate with Let's Encrypt
echo "🔒 Installing SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d lucy.world --non-interactive --agree-tos --email frank@lucy.world

echo "✅ Deployment completed successfully!"

# Setup GitHub auto-deployment
echo ""
echo "🔧 Setting up GitHub auto-deployment..."

# Install webhook service
sudo tee /etc/systemd/system/lucy-webhook.service > /dev/null << EOL
[Unit]
Description=Lucy World Search Webhook Handler
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="WEBHOOK_SECRET=your-webhook-secret-here"
ExecStart=$APP_DIR/venv/bin/python webhook.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Enable webhook service
sudo systemctl daemon-reload
sudo systemctl enable lucy-webhook
sudo systemctl start lucy-webhook

echo ""
echo "🌍 Your application is now available at:"
echo "   https://lucy.world"
echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status lucy-world-search    # Check app status"
echo "   sudo systemctl restart lucy-world-search   # Restart app"
echo "   sudo systemctl status nginx                # Check nginx status"
echo "   sudo journalctl -u lucy-world-search -f    # View app logs"
echo "   sudo tail -f /var/log/nginx/access.log     # View nginx logs"