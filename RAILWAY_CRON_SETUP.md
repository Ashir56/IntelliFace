# Railway Cron Job Setup for IntelliFace

This guide explains how to set up automated snapshot capture on Railway without using Celery.

## 🚀 Deployment Options

### Option 1: Railway Cron Jobs (Recommended)

Railway supports cron jobs natively. Here's how to set it up:

#### 1. Deploy Main Application
```bash
# Deploy your main Django app to Railway
railway login
railway link
railway up
```

#### 2. Create Cron Service
1. In Railway dashboard, create a **new service** in the same project
2. Connect the same GitHub repository
3. Set the service name to `intelliface-cron`
4. Add the same environment variables as your main app

#### 3. Configure Cron Schedule
In Railway dashboard for the cron service:
- Go to **Settings** → **Cron**
- Set schedule: `*/5 * * * *` (every 5 minutes)
- Set command: `python manage.py capture_snapshots --verbose`

**Note**: This command calls the existing `capture_snapshots_for_active_lectures()` function from `apps/core/tasks.py`

#### 4. Environment Variables
Add these to both services:
```
DATABASE_URL=your-postgresql-url
SECRET_KEY=your-secret-key
CRON_SECRET_KEY=your-cron-secret-key
```

### Option 2: External Cron Services

Use external services like cron-job.org, EasyCron, or GitHub Actions.

#### Setup Steps:
1. Deploy your app to Railway
2. Set `CRON_SECRET_KEY` environment variable
3. Configure external service to call:
   ```
   POST https://your-app.railway.app/api/cron/capture-snapshots/
   Headers: X-Cron-Secret: your-cron-secret-key
   ```

#### External Services:
- **cron-job.org**: Free, reliable, web-based
- **EasyCron**: Free tier available
- **GitHub Actions**: Use repository workflows
- **Uptime Robot**: Monitor + cron functionality

### Option 3: GitHub Actions (Free)

Create `.github/workflows/cron-snapshots.yml`:

```yaml
name: Capture Snapshots Cron Job

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:  # Allow manual trigger

jobs:
  capture-snapshots:
    runs-on: ubuntu-latest
    steps:
      - name: Call Snapshot Endpoint
        run: |
          curl -X POST \
            -H "X-Cron-Secret: ${{ secrets.CRON_SECRET_KEY }}" \
            https://your-app.railway.app/api/cron/capture-snapshots/
```

## 🛠 Testing the Setup

### Test Django Management Command
```bash
# Locally - calls capture_snapshots_for_active_lectures() function
python manage.py capture_snapshots --verbose

# On Railway (via Railway CLI)
railway run python manage.py capture_snapshots --verbose
```

### Test HTTP Endpoint
```bash
# Test the cron endpoint - also calls capture_snapshots_for_active_lectures()
curl -X POST \
  -H "X-Cron-Secret: your-secret-key" \
  https://your-app.railway.app/api/cron/capture-snapshots/
```

### Check Logs
```bash
# Railway logs
railway logs --service intelliface-cron

# Or in Railway dashboard → Service → Logs
```

## 📊 Monitoring

### Built-in Logging
The management command logs to:
- Console output (visible in Railway logs)
- Django logging system
- HTTP endpoint returns detailed status

### Log Messages
```
[2024-01-11 10:00:00] Starting snapshot capture task...
Processing lecture 123 for course: Computer Science 101
  ✅ Captured from camera 1 (Front Camera)
  ✅ Captured from camera 2 (Back Camera)
  Lecture 123: 2 snapshots, 0 errors
[2024-01-11 10:00:05] Snapshot capture completed: 2 snapshots captured, 0 errors, 1 active lectures processed
```

### Health Check Endpoint
Monitor cron job health:
```
GET https://your-app.railway.app/api/ml-status/
```

## 🔧 Configuration

### Cron Schedule Options
```bash
# Every 5 minutes
*/5 * * * *

# Every 10 minutes
*/10 * * * *

# Every hour
0 * * * *

# Every 30 minutes during business hours (9 AM - 5 PM)
*/30 9-17 * * 1-5
```

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://...
SECRET_KEY=django-secret-key

# Optional but recommended
CRON_SECRET_KEY=secure-random-string
DEBUG=False

# Logging level
DJANGO_LOG_LEVEL=INFO
```

## 🚨 Troubleshooting

### Common Issues

#### 1. No Active Lectures Found
```
No active lectures found.
```
**Solution**: Ensure lectures are started via `/api/start-attendance/`

#### 2. Camera Connection Failed
```
Error capturing from camera 1: Connection timeout
```
**Solutions**:
- Check camera IP addresses and credentials
- Verify network connectivity from Railway
- Test RTSP URLs manually

#### 3. Permission Denied
```
Error: Invalid or missing secret key
```
**Solution**: Set `CRON_SECRET_KEY` environment variable

#### 4. Database Connection Issues
```
django.db.utils.OperationalError: could not connect to server
```
**Solution**: Verify `DATABASE_URL` environment variable

### Debug Mode
Enable verbose logging in Django settings:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.core': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📈 Performance Considerations

### Resource Usage
- **Memory**: ~50MB per cron execution
- **CPU**: Minimal (snapshot capture only)
- **Network**: Depends on camera count and image size
- **Storage**: Images stored in Railway persistent storage

### Scaling
- Railway cron jobs run on separate containers
- No impact on main application performance
- Can handle multiple concurrent lectures
- Automatic retry on failures

### Cost Optimization
- Railway cron jobs use compute time only when running
- ~5 minutes execution time per hour = minimal cost
- Consider reducing frequency during off-hours

## 🔒 Security

### Best Practices
1. Use strong `CRON_SECRET_KEY`
2. Rotate secrets regularly
3. Monitor cron job logs for suspicious activity
4. Use HTTPS for all external cron calls
5. Limit cron endpoint access by IP if possible

### Secret Management
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in Railway
railway variables set CRON_SECRET_KEY=your-generated-secret
```

## 📚 Additional Resources

- [Railway Cron Jobs Documentation](https://docs.railway.app/deploy/cron-jobs)
- [Django Management Commands](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Cron Expression Generator](https://crontab.guru/)
- [Railway CLI Documentation](https://docs.railway.app/develop/cli)