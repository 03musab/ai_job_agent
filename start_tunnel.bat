@echo off
echo ========================================================
echo Starting Cloudflare Tunnel for AI Job Agent (Port 5000)
echo ========================================================
echo.
echo Make sure 'honcho start' or your Flask app is running!
echo Look for the 'https://*.trycloudflare.com' link below.
echo.
.\cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
