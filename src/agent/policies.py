import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("sre-policy-gatekeeper")

class PolicyGatekeeper:
    """
    Validates all agent-proposed actions against strict security guardrails.
    Rejects arbitrary execution and ensures only allowlisted operations are permitted.
    """

    ALLOWED_ACTION_TYPES = {
        "restart_deployment",
        "scale_deployment",
        "rollback_deployment",
    }

    # Safeguards on replica counts
    MIN_REPLICAS = 1
    MAX_REPLICAS = 10

    # Critical namespaces requiring human-in-the-loop approval
    PROTECTED_SERVICES = {"auth-database", "core-ledger"}

    @classmethod
    def validate_action(cls, action: Dict) -> Tuple[bool, str, bool]:
        """
        Validates an action dictionary.
        Returns: (is_allowed, reason, requires_human_approval)
        """
        action_type = action.get("action_type")
        service_name = action.get("service_name", "")

        # 1. Reject arbitrary commands
        if not action_type or action_type not in cls.ALLOWED_ACTION_TYPES:
            logger.error("Security Violation: Rejected unallowlisted action type '%s'", action_type)
            return False, f"Action '{action_type}' is not allowlisted in SRE execution policy.", False

        # 2. Check protected service boundary
        if service_name in cls.PROTECTED_SERVICES:
            logger.warning("Protected Service: Action on '%s' requires human SRE approval.", service_name)
            return True, f"Action approved but requires human authorization for protected service '{service_name}'.", True

        # 3. Check scaling constraints
        if action_type == "scale_deployment":
            replicas = action.get("replicas")
            if replicas is None or not isinstance(replicas, int):
                return False, "Replicas count must be a valid integer.", False

            if replicas < cls.MIN_REPLICAS or replicas > cls.MAX_REPLICAS:
                return (
                    False,
                    f"Scaling to {replicas} replicas violates policy bounds (Min: {cls.MIN_REPLICAS}, Max: {cls.MAX_REPLICAS}).",
                    False,
                )

        # 4. Check rollback safety
        if action_type == "rollback_deployment":
            # Rollback is safe but logged with high audit priority
            return True, "Rollback permitted within deployment safety policy.", False

        return True, "Action validated and approved by policy gatekeeper.", False

    @classmethod
    def filter_actions(cls, actions: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Filter a list of actions into approved actions and rejected actions."""
        approved = []
        rejected = []

        for act in actions:
            is_allowed, reason, requires_human = cls.validate_action(act)
            record = dict(act)
            record["policy_reason"] = reason
            record["requires_human_approval"] = requires_human

            if is_allowed:
                approved.append(record)
            else:
                rejected.append(record)

        return approved, rejected
