from typing import Dict, Any, List
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# In-memory safe state stores for simulated infrastructure
SIMULATED_FIREWALL_BLOCKLIST: List[Dict[str, Any]] = []
SIMULATED_QUARANTINED_ENDPOINTS: List[Dict[str, Any]] = []
SIMULATED_DISABLED_USERS: List[Dict[str, Any]] = []
SIMULATED_QUARANTINED_EMAILS: List[Dict[str, Any]] = []

class SafeResponseEngine:
    """
    Simulated Response Sandbox Engine.
    Executes containment and remediation actions in a safe simulated sandbox.
    Explicitly tags all actions as SIMULATED.
    """
    
    @staticmethod
    def block_ip_simulation(ip_address: str, reason: str = "Automated SOAR Block") -> Dict[str, Any]:
        """Simulate perimeter firewall IP blocklist insertion"""
        entry = {
            "ip_address": ip_address,
            "reason": reason,
            "blocked_at": datetime.now(timezone.utc).isoformat(),
            "mode": "SIMULATED",
            "action": "FIREWALL_BLOCK_INJECTED"
        }
        SIMULATED_FIREWALL_BLOCKLIST.append(entry)
        logger.info(f"[SIMULATION MODE] Blocked IP {ip_address} in perimeter firewall simulator.")
        return {
            "status": "Success",
            "simulated": True,
            "action": "Perimeter Firewall IP Block",
            "target": ip_address,
            "message": f"SIMULATED: Injected firewall rule to drop all incoming packets from {ip_address}."
        }

    @staticmethod
    def isolate_endpoint_simulation(hostname: str, reason: str = "EDR Host Containment") -> Dict[str, Any]:
        """Simulate host network quarantine via EDR agent"""
        entry = {
            "hostname": hostname,
            "reason": reason,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "mode": "SIMULATED",
            "action": "EDR_HOST_ISOLATED"
        }
        SIMULATED_QUARANTINED_ENDPOINTS.append(entry)
        logger.info(f"[SIMULATION MODE] Host {hostname} isolated via EDR simulator.")
        return {
            "status": "Success",
            "simulated": True,
            "action": "EDR Host Network Isolation",
            "target": hostname,
            "message": f"SIMULATED: Dispatched EDR network isolation policy to host {hostname}."
        }

    @staticmethod
    def disable_user_simulation(username: str, reason: str = "Account Compromise Containment") -> Dict[str, Any]:
        """Simulate IdP account suspension and token revocation"""
        entry = {
            "username": username,
            "reason": reason,
            "disabled_at": datetime.now(timezone.utc).isoformat(),
            "mode": "SIMULATED",
            "action": "IDP_USER_DISABLED"
        }
        SIMULATED_DISABLED_USERS.append(entry)
        logger.info(f"[SIMULATION MODE] Account {username} disabled via IdP simulator.")
        return {
            "status": "Success",
            "simulated": True,
            "action": "Identity Account Suspension",
            "target": username,
            "message": f"SIMULATED: Revoked OAuth refresh tokens and locked IdP credentials for {username}."
        }

    @staticmethod
    def quarantine_email_simulation(indicator: str, reason: str = "Phishing Mailbox Quarantine") -> Dict[str, Any]:
        """Simulate email message purge / quarantine from mailboxes"""
        entry = {
            "indicator": indicator,
            "reason": reason,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "mode": "SIMULATED",
            "action": "MAILBOX_MESSAGE_PURGED"
        }
        SIMULATED_QUARANTINED_EMAILS.append(entry)
        logger.info(f"[SIMULATION MODE] Email matching {indicator} quarantined.")
        return {
            "status": "Success",
            "simulated": True,
            "action": "Mailbox Phishing Quarantine",
            "target": indicator,
            "message": f"SIMULATED: Purged phishing message linking to {indicator} from all enterprise mailboxes."
        }
