# Check status
sudo systemctl status camel-arbitrage.service

# View logs
sudo journalctl -u camel-arbitrage.service -f

# Restart after changes
sudo systemctl restart camel-arbitrage.service

# Stop service
sudo systemctl stop camel-arbitrage.service
