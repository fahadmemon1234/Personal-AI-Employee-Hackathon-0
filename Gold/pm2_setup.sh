#!/bin/bash
# pm2_setup.sh - Script to install and configure PM2 for process management

# Install PM2 globally if not already installed
echo "Installing PM2..."
npm install -g pm2

# Check if installation was successful
if ! command -v pm2 &> /dev/null; then
    echo "PM2 installation failed. Please install Node.js and npm first."
    exit 1
fi

echo "PM2 installed successfully!"

# Navigate to the project directory
cd "$(dirname "$0")"

# Start all processes defined in ecosystem.config.js
echo "Starting all processes with PM2..."
pm2 start ecosystem.config.js

# Save the PM2 configuration for auto-start on boot
echo "Saving PM2 configuration..."
pm2 save

# Enable PM2 startup script to run on system boot
echo "Setting up PM2 startup script..."
pm2 startup

echo "PM2 setup complete!"
echo "Your processes are now running and will restart automatically on system boot."
echo ""
echo "Useful PM2 commands:"
echo "  pm2 status          # View status of all processes"
echo "  pm2 logs            # View logs of all processes"
echo "  pm2 restart all     # Restart all processes"
echo "  pm2 stop all        # Stop all processes"
echo "  pm2 delete all      # Delete all processes from PM2"