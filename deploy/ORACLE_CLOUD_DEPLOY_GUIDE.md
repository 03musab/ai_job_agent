# 🚀 Oracle Cloud "Always Free" Deployment Guide

Follow these steps to host your **AI Job Agent** on an Oracle Cloud "Always Free" Ubuntu server.

---

## Step 1: Create Your Free Oracle Cloud VM

1. Sign in to [Oracle Cloud Console](https://cloud.oracle.com/).
2. Go to **Compute** -> **Instances** -> Click **Create Instance**.
3. Fill in the instance details:
   - **Name**: `ai-job-agent-server`
   - **Image**: Click **Change image** -> Select **Ubuntu 22.04** or **Ubuntu 24.04**.
   - **Shape**: Click **Change shape**:
     - Choose **Ampere (ARM)** -> **VM.Standard.A1.Flex** (Always Free Eligible: allocate 2 or 4 OCPUs and 12–24 GB RAM for $0/mo).
     - *(Alternative if ARM is out of capacity in your region: Choose AMD `VM.Standard.E2.1.Micro` with 1 OCPU, 1 GB RAM)*.
   - **Networking**: Keep defaults (Create new Virtual Cloud Network).
   - **Add SSH keys**: 
     - Select **Generate a key pair for me** and download both the **Private Key** (`.key`) and **Public Key**.
4. Click **Create**. Within 1–2 minutes, your instance will show **Running** and give you a **Public IP Address** (e.g., `129.153.x.x`).

---

## Step 2: Open Ingress Ports in Oracle Cloud Console (Crucial!)

By default, Oracle Cloud blocks incoming web traffic. You must allow ports **80 (HTTP)** and **443 (HTTPS)**:

1. On your Instance Details page, click your **Subnet** name (under Primary VNIC).
2. Click on the **Default Security List for...**.
3. Under **Ingress Rules**, click **Add Ingress Rules**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `80,443`
   - Click **Add Ingress Rules**.

---

## Step 3: Connect via SSH

From your local computer terminal (PowerShell or Bash), run:

```bash
ssh -i /path/to/your/downloaded_private_key.key ubuntu@<YOUR_PUBLIC_IP>
```

---

## Step 4: Transfer Your Project Files

On your local computer, push your repository to GitHub (recommended) or copy files directly:

### Option A: Via GitHub (Recommended)
On your server:
```bash
git clone https://github.com/<your-username>/ai_job_agent.git /home/ubuntu/ai_job_agent
cd /home/ubuntu/ai_job_agent
```

### Option B: Via SCP from your local machine
```bash
scp -i /path/to/key.key -r C:\Users\musab\Desktop\ai_job_agent ubuntu@<YOUR_PUBLIC_IP>:/home/ubuntu/ai_job_agent
```

---

## Step 5: Configure Environment Variables

Create your `.env` on the server:
```bash
cd /home/ubuntu/ai_job_agent
nano .env
```
Paste your production configuration:
```env
FLASK_ENV=production
SECRET_KEY=generate_a_random_secure_secret_string_here
DATABASE_URL=sqlite:////home/ubuntu/ai_job_agent/learning_paths.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Your AI & Scraper keys
CEREBRAS_API_KEY=your_key_here
# Add any other keys from your local .env
```
Save with `Ctrl+O`, then `Enter`, then exit with `Ctrl+X`.

---

## Step 6: Run the 1-Step Setup Script

Run the automated setup script we created:

```bash
cd /home/ubuntu/ai_job_agent
chmod +x deploy/setup_server.sh
./deploy/setup_server.sh
```

This script will automatically:
- Install Python, Redis, Nginx, and Chrome/Chromium for Selenium.
- Create your Python virtual environment and install dependencies.
- Configure Redis to start automatically.
- Setup and start the 3 background services (`ai-job-web`, `ai-job-worker`, `ai-job-beat`).
- Setup Nginx to reverse-proxy port 80 to Gunicorn.
- Open firewall ports.

---

## Step 7: Verify Everything is Live!

Open your browser and navigate to:
```
http://<YOUR_PUBLIC_IP>
```

### Useful Management Commands:
- **Check Web Status**: `sudo systemctl status ai-job-web`
- **Check Worker Status**: `sudo systemctl status ai-job-worker`
- **Check Scheduler (Beat) Status**: `sudo systemctl status ai-job-beat`
- **View Live Web Logs**: `journalctl -u ai-job-web -f`
- **Restart App after code changes**: `sudo systemctl restart ai-job-web ai-job-worker`

---

## Step 8 (Optional): Add Free Custom Domain & HTTPS (SSL)

If you own a domain (e.g. `jobs.yourdomain.com`):
1. Point an `A` record for your domain to your Oracle Public IP.
2. On your server, run:
```bash
sudo certbot --nginx -d jobs.yourdomain.com
```
Certbot will configure free auto-renewing HTTPS/SSL in 30 seconds!
