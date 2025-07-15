#!/bin/bash
# Update cron job for auto-git push

# Remove old cron job and add new one
(crontab -l | grep -v "Research-Analytics-Services-Clean") | crontab -

# Add new cron job - runs every 15 minutes
(crontab -l 2>/dev/null; echo "*/15 * * * * cd '/Users/mikaeleage/Research & Analytics Services' && ./auto_git_push.sh >> auto_git.log 2>&1") | crontab -

echo "✅ Updated cron job to run every 15 minutes"
echo "📁 Working directory: /Users/mikaeleage/Research & Analytics Services"
echo "📝 Logs will be saved to: auto_git.log"

# Show the new crontab
echo ""
echo "Current cron jobs:"
crontab -l