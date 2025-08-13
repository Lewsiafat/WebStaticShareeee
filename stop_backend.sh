#!/bin/bash
PORT=8000
echo "Attempting to stop backend server on port $PORT..."

# Find the PID of the process listening on the port
PID=$(lsof -t -i :$PORT)

if [ -z "$PID" ]; then
  echo "No process found listening on port $PORT."
else
  echo "Found process with PID $PID listening on port $PORT. Killing it..."
  kill -9 $PID
  echo "Process $PID killed."
fi
