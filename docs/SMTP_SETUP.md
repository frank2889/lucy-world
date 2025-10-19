# SMTP Configuration for Lucy World Email

## Your App Password

```text
ykar ermc qrcl rnnr
```

(Format for .env file: `ykarepmcqrclrnnr` - remove spaces)

## Step-by-Step Setup on DigitalOcean

### 1. SSH into Your Server

```bash
# Use your actual server credentials
ssh root@your-server-ip
# OR
ssh your-username@your-server-ip
```

### 2. Navigate to App Directory

```bash
cd /var/www/lucy-world-search
```

### 3. Create/Edit Environment File

```bash
sudo nano .env
```

### 4. Add SMTP Configuration

Add these lines to the `.env` file:

```bash
# SMTP Configuration for Magic Link Emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=marketing@lucy.world
SMTP_PASSWORD=ykarepmcqrclrnnr
SMTP_FROM=no-reply@lucy.world
SMTP_REPLY_TO=support@lucy.world
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### 5. Save and Exit

- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

### 6. Restart the Service

```bash
sudo systemctl restart lucy-world-search
sudo systemctl restart nginx
```

### 7. Test the Email

Go to https://lucy.world and try to log in with any email address. You should receive a magic link!

## Troubleshooting

If emails don't work:

1. Check the logs:

```bash
sudo journalctl -u lucy-world-search -f
```

2. Verify environment variables are loaded:

```bash
sudo systemctl show lucy-world-search --property=Environment
```

3. Make sure the .env file is in the correct location and readable by the service

## Security Note

**IMPORTANT:** Never commit the `.env` file with real credentials to Git! It's already in `.gitignore`.

## Status

- ✅ SMTP configured in DigitalOcean App Platform (Oct 8, 2025)
- ✅ Using Gmail SMTP with marketing@lucy.world
- ✅ All environment variables set
