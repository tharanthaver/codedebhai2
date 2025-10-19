#!/bin/bash

# CodeDeBhai Monthly Rollover System - Linux VPS Version
# This script runs the production rollover system automatically

# Change to the project directory (update this path for your VPS)
cd /var/www/codedebhai || cd /home/ubuntu/codedebhai || cd /root/codedebhai

# Activate virtual environment if using one
# source venv/bin/activate

# Set environment variables if not already set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Log the start time
echo "[$(date)] Starting Monthly Credit Rollover System" >> rollover_scheduler.log

# Run the production rollover system
python3 production_rollover_system.py >> rollover_scheduler.log 2>&1

# Log completion
echo "[$(date)] Monthly Credit Rollover System completed" >> rollover_scheduler.log
echo "=====================================" >> rollover_scheduler.log

# Optional: Send notification (uncomment if needed)
# curl -X POST "https://api.telegram.org/bot<your_bot_token>/sendMessage" \
#      -d chat_id="<your_chat_id>" \
#      -d text="Monthly rollover completed successfully"

exit 0
