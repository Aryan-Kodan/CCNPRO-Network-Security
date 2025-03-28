# config.py

ALLOWED_IPS = ["127.0.0.1"]
CRITICAL_IPS = ["127.0.0.1"]  # Add management IPs here
CRITICAL_PORTS = ["22", "443"]  # SSH and HTTPS

FAILSAFE_MODE = False  # When True, no block/unblock is allowed
CURRENT_IP = "192.168.1.50"  # Set this to the IP you'll use for testing (or fetch dynamically)
SAFE_MODE = False   # default is off
FAILSAFE_LOG_PATH = "./logger/failsafe.log"
