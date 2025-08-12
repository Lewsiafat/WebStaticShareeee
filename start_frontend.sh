#!/bin/bash
cd frontend
npm run serve &
echo "Vue.js frontend started in background on port 8080 (default)."
echo "PID: $!"