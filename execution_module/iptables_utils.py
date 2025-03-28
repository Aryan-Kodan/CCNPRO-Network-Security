# execution_module/iptables_utils.py

import subprocess
from logger.custom_logger import log_event

DUMMY_CHAIN = "NSMS_DUMMY"

def run_iptables_cmd(args):
    """Runs an iptables command safely."""
    cmd = ["sudo", "iptables"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_event("error", f"iptables error: {result.stderr.strip()}")
        return False, result.stderr.strip()
    return True, result.stdout.strip()

def ensure_dummy_chain():
    """Create dummy chain if it doesn't exist."""
    success, _ = run_iptables_cmd(["-L", DUMMY_CHAIN])
    if not success:
        run_iptables_cmd(["-N", DUMMY_CHAIN])
        log_event("system", f"Dummy chain {DUMMY_CHAIN} created")
