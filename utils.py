"""
Utility functions for the Asana API
"""
import uuid


def generate_gid() -> str:
    """
    Generate a unique GID (Globally Unique Identifier) using UUID4.
    This function should be used for all create operations to auto-generate GIDs.
    """
    return str(uuid.uuid4())

