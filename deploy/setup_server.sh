#!/usr/bin/env bash
set -e

echo "=============================================="
echo " Starting AI Job Agent Production Setup on Ubuntu"
echo "=============================================="

# 1. Update system packages
echo "--> Updating system packages..."
sudo apt-get update -y
sudo apt-get install -y software-properties-common curl wget git unzip

# 2. Install Python 3, pip, venv, Redis, and Nginx
echo "--> Installing Python 3, Redis, and Nginx..."
sudo apt-get install -y python3 python3-pip python3-venv redis-server nginx

# 3. Install Headless Chrome / Chromium dependencies for Selenium
echo "--> Installing Chrome & scraping dependencies..."
sudo apt-get install -y libnss3 libatk1.0-0 libasound2 libgbm1 libpangocairo-1.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    if ! command -v google-chrome &> /dev/null; then
        echo "Installing Google Chrome (x86_64)..."
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
        rm -f google-chrome-stable_current_amd64.deb
    fi
else
    echo "Installing Chromium for ARM64 / other architecture..."
    sudo apt-get install -y chromium-browser chromium-chromedriver
fi

# 4. Enable and start Redis
echo "--> Starting and enabling Redis..."
sudo systemctl enable redis-server
sudo systemctl restart redis-server

# 5. Setup Python Virtual Environment
APP_DIR="/home/ubuntu/ai_job_agent"
cd "$APP_DIR"

echo "--> Setting up Python virtual environment..."
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi

echo "--> Installing Python dependencies..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 6. Ensure uploads and data directories exist
mkdir -p "$APP_DIR/uploads/csv_repository"
mkdir -p "$APP_DIR/uploads/company-logos"
mkdir -p "$APP_DIR/instance"
chown -R ubuntu:ubuntu "$APP_DIR/uploads" "$APP_DIR/instance"

# 7. Configure Nginx
echo "--> Configuring Nginx reverse proxy..."
sudo cp "$APP_DIR/deploy/nginx/ai_job_agent.conf" /etc/nginx/sites-available/ai_job_agent.conf
sudo ln -sf /etc/nginx/sites-available/ai_job_agent.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. Install and configure systemd services
echo "--> Registering systemd services..."
sudo cp "$APP_DIR/deploy/systemd/ai-job-web.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/systemd/ai-job-worker.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/systemd/ai-job-beat.service" /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable ai-job-web ai-job-worker ai-job-beat
sudo systemctl restart ai-job-web ai-job-worker ai-job-beat

# 9. Configure UFW Firewall (Oracle / Ubuntu internal firewall)
echo "--> Configuring firewall (ports 22, 80, 443)..."
sudo ufw allow OpenSSH || true
sudo ufw allow 'Nginx Full' || true
sudo ufw --force enable || true

# Oracle Linux / Ubuntu iptables fix for Oracle Cloud (often blocks port 80/443 in iptables by default)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT || true
sudo netfilter-persistent save || true

echo "=============================================="
echo " Setup complete!"
echo " Web status:    sudo systemctl status ai-job-web"
echo " Worker status: sudo systemctl status ai-job-worker"
echo " Beat status:   sudo systemctl status ai-job-beat"
echo " View logs:     journalctl -u ai-job-web -f"
echo "=============================================="
