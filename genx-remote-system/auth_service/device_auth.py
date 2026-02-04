import hmac
import hashlib
import os

# It is recommended to load the secret key from environment variables
# for production environments. For example:
# SECRET_KEY = os.environ.get("DEVICE_SECRET_KEY", "default-secret-key")
SECRET_KEY = "your-super-secret-key"  # Replace with a secure key in a real environment

def generate_device_fingerprint(build_number: str) -> str:
    """
    Generates a secure HMAC-SHA256 hash of the device build number.

    Args:
        build_number: The build number of the device.

    Returns:
        A hex-encoded HMAC-SHA256 hash.
    """
    key = SECRET_KEY.encode('utf-8')
    message = build_number.encode('utf-8')

    # Create an HMAC-SHA256 hash
    signature = hmac.new(key, message, hashlib.sha256)

    return signature.hexdigest()

def verify_device_fingerprint(build_number: str, fingerprint: str) -> bool:
    """
    Verifies if the provided fingerprint matches the build number.

    Args:
        build_number: The build number of the device.
        fingerprint: The fingerprint to verify.

    Returns:
        True if the fingerprint is valid, False otherwise.
    """
    expected_fingerprint = generate_device_fingerprint(build_number)

    # Use hmac.compare_digest for secure comparison to prevent timing attacks
    return hmac.compare_digest(expected_fingerprint, fingerprint)

if __name__ == '__main__':
    # Example Usage
    device_build_number = "15.1.1.109SP06(OP001PF001AZ)"

    # Generate a fingerprint
    generated_fingerprint = generate_device_fingerprint(device_build_number)
    print(f"Device Build Number: {device_build_number}")
    print(f"Generated Fingerprint: {generated_fingerprint}")

    # Verify the fingerprint
    is_valid = verify_device_fingerprint(device_build_number, generated_fingerprint)
    print(f"Verification Result: {'Valid' if is_valid else 'Invalid'}")

    # Example of an invalid verification
    invalid_fingerprint = "some-invalid-fingerprint"
    is_valid = verify_device_fingerprint(device_build_number, invalid_fingerprint)
    print(f"Verification with invalid fingerprint: {'Valid' if is_valid else 'Invalid'}")