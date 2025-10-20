# DigitalOcean Deployment Fix - lucy-world

## Issue Diagnosed
**Error**: "No application module specified" + "connection refused" on readiness probe

**Root Cause**: Hard-coded `PORT: "8080"` environment variable in `.do/app.yaml` was conflicting with DigitalOcean's dynamic `$PORT` assignment, preventing Gunicorn from binding to the correct port.

## Changes Applied

### 1. Removed PORT Override from `.do/app.yaml`
**Before:**
```yaml
envs:
  - key: FLASK_ENV
    value: production
  - key: PORT
    value: "8080"  # ❌ CONFLICT!
  - key: PYTHONUNBUFFERED
    value: "1"
```

**After:**
```yaml
envs:
  - key: FLASK_ENV
    value: production
  - key: PYTHONUNBUFFERED
    value: "1"
  # PORT now injected by DigitalOcean automatically
```

### 2. Verified Correct Configuration

#### `.do/app.yaml`:
```yaml
run_command: gunicorn scripts.wsgi:app --config scripts/gunicorn.conf.py
environment_slug: python
health_check:
  http_path: /health
```

#### `Procfile`:
```
web: gunicorn scripts.wsgi:app --config scripts/gunicorn.conf.py
```

#### `scripts/gunicorn.conf.py`:
```python
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
wsgi_app = "scripts.wsgi:app"
chdir = str(PROJECT_ROOT)
workers = 2
```

#### `scripts/wsgi.py`:
```python
from backend import create_app
application = create_app()
app = application  # gunicorn expects 'app'
```

## Expected Deployment Behavior

### Runtime Logs Should Show:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Starting Lucy World Search Gunicorn workers
[INFO] Listening at: http://0.0.0.0:<DYNAMIC_PORT>
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXXXX
[INFO] Booting worker with pid: XXXXX
```

### Health Check:
```bash
curl -sfS https://lucy.world/health
# Should return: HTTP 200 OK
```

## Verification Checklist

- [x] Removed hard-coded PORT from environment variables
- [x] Confirmed Gunicorn config reads PORT from environment
- [x] Verified Procfile uses correct command
- [x] Verified .do/app.yaml run_command is correct
- [x] Confirmed /health endpoint exists in backend
- [x] Committed and pushed changes to trigger rebuild

## Console Actions Required

In DigitalOcean App Platform Console:

1. Navigate to: **lucy-world → Settings → Components → web**
2. Verify:
   - **Component Type**: Web Service
   - **Environment**: Python
   - **Run Command**: Either set to `gunicorn scripts.wsgi:app --config scripts/gunicorn.conf.py` OR clear it to use Procfile
3. Click **"Deploy"** to trigger rebuild

## Fallback Commands (if needed)

If deployment still fails, use doctl CLI:

```bash
# Update app spec
doctl apps update "$DO_APP_ID" --spec .do/app.yaml

# Force deployment
doctl apps create-deployment "$DO_APP_ID"
```

## Success Criteria

✅ No "No application module specified" error
✅ Readiness probe succeeds (no connection refused)
✅ Gunicorn workers boot and bind to $PORT
✅ Service returns HTTP 200 on /health
✅ Application accessible at https://lucy.world

## Commit Details

**Commit**: fix(app-platform): use gunicorn scripts.wsgi:app and drop PORT override
**Branch**: main
**Status**: Pushed and deployment triggered
