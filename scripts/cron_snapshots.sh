#!/bin/bash

# Railway Cron Job Script for Snapshot Capture
# This script runs the Django management command which calls capture_snapshots_for_active_lectures()

echo "Starting snapshot capture at $(date)"

# Run the Django management command (calls existing task function)
python manage.py capture_snapshots --verbose

echo "Snapshot capture completed at $(date)"