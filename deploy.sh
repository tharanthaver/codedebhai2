#!/bin/bash

# VPS Deployment Script for CodeDeBhai with Celery + Redis
# Run this script on your VPS to set up the application

set -e

echo "🚀 Starting VPS deployment for CodeDeBhai..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python and pip..."
sudo apt install python3 python3-pip python3-venv -y

# Install Redis Server
echo "🔴 Installing Redis Server..."
sudo apt install redis-server -y

# Configure Redis
echo "⚙️ Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Supervisor for process management
echo "👮 Installing Supervisor..."
sudo apt install supervisor -y

# Create application directory
APP_DIR="/var/www/codedebhai"
echo "📁 Creating application directory at $APP_DIR..."
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Navigate to app directory
cd $APP_DIR

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p solved_files temp logs

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please update .env file with your production values"
fi

# Create Gunicorn configuration
echo "🦄 Creating Gunicorn configuration..."
cat > gunicorn.conf.py << 'EOF'
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
user = "www-data"
group = "www-data"
pidfile = "/var/run/gunicorn.pid"
accesslog = "/var/www/codedebhai/logs/access.log"
errorlog = "/var/www/codedebhai/logs/error.log"
loglevel = "info"
EOF

# Create systemd service for Flask app
echo "🔧 Creating systemd service for Flask app..."
sudo tee /etc/systemd/system/codedebhai.service > /dev/null << EOF
[Unit]
Description=CodeDeBhai Flask Application
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/codedebhai
Environment=PATH=/var/www/codedebhai/venv/bin
ExecStart=/var/www/codedebhai/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Celery worker
echo "🔧 Creating systemd service for Celery worker..."
sudo tee /etc/systemd/system/celery-worker.service > /dev/null << EOF
[Unit]
Description=Celery Worker Service
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/codedebhai
Environment=PATH=/var/www/codedebhai/venv/bin
ExecStart=/var/www/codedebhai/venv/bin/celery multi start worker1 -A celery_config --pidfile=/var/run/celery/%%n.pid --logfile=/var/www/codedebhai/logs/celery_worker.log --loglevel=info
ExecStop=/var/www/codedebhai/venv/bin/celery multi stopwait worker1 --pidfile=/var/run/celery/%%n.pid
ExecReload=/var/www/codedebhai/venv/bin/celery multi restart worker1 -A celery_config --pidfile=/var/run/celery/%%n.pid --logfile=/var/www/codedebhai/logs/celery_worker.log --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Celery beat
echo "🔧 Creating systemd service for Celery beat..."
sudo tee /etc/systemd/system/celery-beat.service > /dev/null << EOF
[Unit]
Description=Celery Beat Service
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/codedebhai
Environment=PATH=/var/www/codedebhai/venv/bin
ExecStart=/var/www/codedebhai/venv/bin/celery -A celery_config beat --pidfile=/var/run/celery/beat.pid --logfile=/var/www/codedebhai/logs/celery_beat.log --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create directories for Celery
echo "📁 Creating Celery directories..."
sudo mkdir -p /var/run/celery
sudo chown -R www-data:www-data /var/run/celery

# Create log directory
sudo mkdir -p /var/www/codedebhai/logs
sudo chown -R www-data:www-data /var/www/codedebhai/logs

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y

# Create Nginx configuration
echo "🔧 Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/codedebhai > /dev/null << EOF
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Increase timeout for large file uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Increase max body size for PDF uploads
        client_max_body_size 50M;
    }

    location /static {
        alias /var/www/codedebhai/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/codedebhai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Create a startup script
echo "🔧 Creating startup script..."
cat > start_services.sh << 'EOF'
#!/bin/bash

# Start Redis
sudo systemctl start redis-server

# Start Flask app
sudo systemctl start codedebhai

# Start Celery worker
sudo systemctl start celery-worker

# Start Celery beat
sudo systemctl start celery-beat

# Start Nginx
sudo systemctl start nginx

echo "✅ All services started successfully!"
EOF

chmod +x start_services.sh

# Create a stop script
echo "🔧 Creating stop script..."
cat > stop_services.sh << 'EOF'
#!/bin/bash

# Stop all services
sudo systemctl stop nginx
sudo systemctl stop celery-beat
sudo systemctl stop celery-worker
sudo systemctl stop codedebhai
sudo systemctl stop redis-server

echo "🛑 All services stopped!"
EOF

chmod +x stop_services.sh

# Create a restart script
echo "🔧 Creating restart script..."
cat > restart_services.sh << 'EOF'
#!/bin/bash

# Restart all services
sudo systemctl restart redis-server
sudo systemctl restart codedebhai
sudo systemctl restart celery-worker
sudo systemctl restart celery-beat
sudo systemctl restart nginx

echo "🔄 All services restarted!"
EOF

chmod +x restart_services.sh

# Set proper permissions
echo "🔒 Setting proper permissions..."
sudo chown -R www-data:www-data /var/www/codedebhai
sudo chmod -R 755 /var/www/codedebhai

# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
echo "🔧 Enabling services to start on boot..."
sudo systemctl enable redis-server
sudo systemctl enable codedebhai
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
sudo systemctl enable nginx

echo "✅ VPS deployment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with production values"
echo "2. Update the Nginx configuration with your domain name"
echo "3. Run './start_services.sh' to start all services"
echo "4. Check service status with: sudo systemctl status [service-name]"
echo "5. View logs with: sudo journalctl -u [service-name] -f"
echo ""
echo "🔧 Available commands:"
echo "- ./start_services.sh   - Start all services"
echo "- ./stop_services.sh    - Stop all services"
echo "- ./restart_services.sh - Restart all services"
echo ""
echo "📊 Monitor services:"
echo "- Redis: sudo systemctl status redis-server"
echo "- Flask: sudo systemctl status codedebhai"
echo "- Celery Worker: sudo systemctl status celery-worker"
echo "- Celery Beat: sudo systemctl status celery-beat"
echo "- Nginx: sudo systemctl status nginx"
