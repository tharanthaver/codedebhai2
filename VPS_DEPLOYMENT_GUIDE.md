# CodeDeBhai VPS Deployment Guide
## Monthly Rollover Scheduler Integration

### 🎯 Testing Results Summary

✅ **All scheduler integration tests PASSED!**
- ✅ Scheduler initializes correctly with Flask app
- ✅ Background scheduler runs automatically
- ✅ Manual rollover endpoints work perfectly
- ✅ Database connections are stable
- ✅ Environment configuration is correct
- ✅ Next scheduled run: **August 1st, 2025 at 2:00 AM**

---

## 🚀 VPS Deployment Steps

### 1. **Upload Your Code to VPS**
```bash
# Upload the entire project directory to your VPS
scp -r flaskdeployment-main/ user@your-vps-ip:/var/www/codedebhai/
```

### 2. **Install Dependencies**
```bash
# On your VPS
cd /var/www/codedebhai/
pip install -r requirements.txt

# Verify APScheduler is installed
python -c "import apscheduler; print('✅ APScheduler installed')"
```

### 3. **Configure Environment Variables**
```bash
# Create/update .env file on VPS
nano .env

# Ensure these are set for production:
ROLLOVER_ENABLED=true
ROLLOVER_DRY_RUN=false
ROLLOVER_NOTIFICATION_EMAIL=your-admin@codedebhai.com
```

### 4. **Test Integration on VPS**
```bash
# Run the integration test on VPS
python test_scheduler_integration.py
```

### 5. **Deploy with Process Manager**

#### Option A: Using PM2 (Recommended)
```bash
# Install PM2
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'codedebhai',
    script: 'app.py',
    interpreter: 'python3',
    env: {
      PORT: 5000,
      NODE_ENV: 'production'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    log_file: 'logs/app.log',
    error_file: 'logs/error.log',
    out_file: 'logs/out.log'
  }]
};
EOF

# Start the application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Option B: Using Gunicorn
```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Create gunicorn startup script
cat > start_gunicorn.sh << EOF
#!/bin/bash
cd /var/www/codedebhai/
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 app:app
EOF

chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

### 6. **Monitor Scheduler Status**

Once deployed, you can monitor the scheduler using these endpoints:

#### Check Scheduler Status
```bash
curl http://your-domain.com/admin/rollover/status
```

Expected Response:
```json
{
  "scheduler_running": true,
  "next_run_time": "2025-08-01T02:00:00+05:30",
  "rollover_enabled": true
}
```

#### Test Rollover System
```bash
curl http://your-domain.com/admin/rollover/test
```

#### Manual Rollover (Emergency)
```bash
curl -X POST http://your-domain.com/admin/rollover/manual
```

---

## 🔧 Production Configuration

### Environment Variables for Production
```env
# Production Rollover Configuration
ROLLOVER_ENABLED=true
ROLLOVER_DRY_RUN=false
ROLLOVER_NOTIFICATION_EMAIL=admin@codedebhai.com
ROLLOVER_BACKUP_ENABLED=true
ROLLOVER_LOG_LEVEL=INFO
ROLLOVER_MAX_RETRIES=3
ROLLOVER_ALERT_THRESHOLD=1000
ROLLOVER_ENABLE_ALERTS=true

# Schedule (1st of every month at 2:00 AM)
ROLLOVER_DAY_OF_MONTH=1
ROLLOVER_HOUR=2
ROLLOVER_MINUTE=0
```

### Log Files to Monitor
- `logs/rollover_YYYYMMDD_HHMMSS.log` - Monthly rollover logs
- `logs/app.log` - General application logs
- `rollover_scheduler.log` - Scheduler activity logs

---

## 📊 Monthly Rollover Logic

### How It Works:
1. **Automatic Execution**: Runs every 1st of the month at 2:00 AM
2. **User Analysis**: Checks all users with credits > 0
3. **Plan Eligibility**: 
   - ✅ **Monthly/Power plans** paid within 1 month → Credits rolled over
   - ❌ **Starter plans** or expired plans → Credits expire
4. **Business Protection**: Prevents credit abuse while rewarding loyal customers

### Expected Behavior:
- **Monthly Plan Users**: Keep their credits
- **Power Plan Users**: Keep their credits + priority access
- **Starter Plan Users**: Credits expire after 1 month
- **Inactive Users**: Credits expire

---

## 🚨 Monitoring & Alerts

### What to Monitor:
1. **Scheduler Status**: Check `/admin/rollover/status` daily
2. **Log Files**: Monitor for errors in rollover logs
3. **Database**: Ensure credit updates are working
4. **Email Notifications**: Admin emails after each rollover

### Alert Thresholds:
- **1000+ credits** processed → High activity alert
- **Failed rollovers** → Immediate investigation needed
- **Scheduler stopped** → Critical system issue

---

## 🛠️ Troubleshooting

### Common Issues:

#### 1. Scheduler Not Starting
```bash
# Check if ROLLOVER_ENABLED=true
grep ROLLOVER_ENABLED .env

# Test scheduler initialization
python test_scheduler_integration.py
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
python -c "from db_helper import DatabaseHelper; db = DatabaseHelper(); print('✅ DB Connected')"
```

#### 3. Environment Variables Missing
```bash
# Check all required variables
python -c "
import os
required = ['SUPABASE_URL', 'SUPABASE_KEY', 'SECRET_KEY']
for var in required:
    print(f'{var}: {\"✅\" if os.getenv(var) else \"❌\"}')"
```

### Emergency Commands:
```bash
# Force manual rollover
curl -X POST http://localhost:5000/admin/rollover/manual

# Check scheduler status
curl http://localhost:5000/admin/rollover/status

# View recent logs
tail -f logs/rollover_*.log
```

---

## ✅ Deployment Checklist

- [ ] Code uploaded to VPS
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured
- [ ] Integration tests pass on VPS
- [ ] Application running with process manager
- [ ] Scheduler endpoints responding
- [ ] Log files being created
- [ ] Database connections stable
- [ ] Admin email configured
- [ ] Monitoring setup

---

## 🎉 Success Criteria

Your deployment is successful when:
1. ✅ Application starts without errors
2. ✅ Scheduler shows next run time: August 1st, 2025
3. ✅ `/admin/rollover/status` returns `scheduler_running: true`
4. ✅ Manual rollover works via API
5. ✅ Log files are being created
6. ✅ Database operations are functioning

**Your scheduler is now production-ready! 🚀**

The system will automatically handle monthly credit rollovers, protecting your business model while providing excellent user experience.
