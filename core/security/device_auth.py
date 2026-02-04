import hashlib

def hash_device_id(device_id: str) -> str:
    """
    Hashes the device ID using SHA-256.
    """
    return hashlib.sha256(device_id.encode()).hexdigest()

def verify_device_id(device_id: str, hashed_device_id: str) -> bool:
    """
    Verifies the given device ID against a stored hash.
    """
    return hash_device_id(device_id) == hashed_device_id