#!/bin/bash

# Copy PDF templates to memory mount on container startup
echo "Setting up memory mount for PDF templates..."

# Create memory mount directories (appuser should have write access to /dev/shm)
mkdir -p /dev/shm/autocusto/static/processos
mkdir -p /dev/shm/autocusto/static/protocolos

# Copy PDF templates to memory mount
echo "Copying processos PDFs to memory..."
cp -r /home/appuser/app/static/autocusto/processos/* /dev/shm/autocusto/static/processos/ 2>/dev/null || true

echo "Copying protocolos PDFs to memory..."
cp -r /home/appuser/app/static/autocusto/protocolos/* /dev/shm/autocusto/static/protocolos/ 2>/dev/null || true

echo "Memory mount dsetup complete. PDF templates available in /dev/shm/autocusto/static/"

# Execute the original command
exec "$@"