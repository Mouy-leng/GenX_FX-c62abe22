import firebase_admin
from firebase_admin import credentials, firestore
import os
import datetime

# --- Firebase Initialization ---
# For secure setup, the path to your Firebase service account key should be
# set as an environment variable.
# Example: export FIREBASE_SERVICE_ACCOUNT_KEY="/path/to/your/serviceAccountKey.json"

SERVICE_ACCOUNT_KEY_PATH = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
FIREBASE_PROJECT_ID = "genx-firebase"  # Your Firebase Project ID

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK.
    Returns the Firestore client if initialization is successful, otherwise None.
    """
    if not SERVICE_ACCOUNT_KEY_PATH:
        print("Error: The FIREBASE_SERVICE_ACCOUNT_KEY environment variable is not set.")
        print("Please provide the path to your Firebase service account key.")
        return None

    if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
        print(f"Error: The service account key file was not found at: {SERVICE_ACCOUNT_KEY_PATH}")
        return None

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_PROJECT_ID,
        })
        print("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

# --- Session Management Functions ---

def create_user_session(db, user_id: str, github_username: str, build_number: str, fingerprint: str) -> str:
    """
    Creates a new user session document in Firestore.

    Args:
        db: The Firestore client.
        user_id: The GitHub user ID.
        github_username: The GitHub username.
        build_number: The device build number.
        fingerprint: The device fingerprint.

    Returns:
        The ID of the newly created session document.
    """
    sessions_ref = db.collection('sessions')

    # Session will be active for 1 hour
    created_at = datetime.datetime.now(datetime.timezone.utc)
    expires_at = created_at + datetime.timedelta(hours=1)

    session_data = {
        "userId": user_id,
        "githubUsername": github_username,
        "deviceBuildNumber": build_number,
        "deviceFingerprint": fingerprint,
        "createdAt": created_at,
        "expiresAt": expires_at,
        "isActive": True
    }

    # Add a new document with a generated ID
    update_time, session_ref = sessions_ref.add(session_data)
    print(f"Created new session with ID: {session_ref.id}")
    return session_ref.id

def validate_session(db, session_id: str) -> bool:
    """
    Validates a session by checking if it exists, is active, and has not expired.

    Args:
        db: The Firestore client.
        session_id: The ID of the session to validate.

    Returns:
        True if the session is valid, False otherwise.
    """
    session_ref = db.collection('sessions').document(session_id)
    session_doc = session_ref.get()

    if not session_doc.exists:
        print(f"Session {session_id} not found.")
        return False

    session_data = session_doc.to_dict()
    now = datetime.datetime.now(datetime.timezone.utc)

    if not session_data.get("isActive"):
        print(f"Session {session_id} is not active.")
        return False

    if now > session_data.get("expiresAt"):
        print(f"Session {session_id} has expired.")
        # Optionally, you could update the document to set isActive to False
        # session_ref.update({"isActive": False})
        return False

    print(f"Session {session_id} is valid.")
    return True

if __name__ == '__main__':
    # --- Example Usage ---
    # This is a demonstration. In a real application, you would not run this directly.

    print("--- Firebase Client Demonstration ---")

    # Initialize Firebase
    db_client = initialize_firebase()

    if db_client:
        # Example data
        example_user_id = "github_user_123"
        example_username = "testuser"
        example_build_number = "15.1.1.109SP06(OP001PF001AZ)"
        example_fingerprint = "9d6c3536cd81ed1b63d684fe8f68a8e79694e8d97b0c1fe6d338813304df9c8c"

        # 1. Create a new session
        print("\n--- Step 1: Creating a user session ---")
        session_id = create_user_session(
            db=db_client,
            user_id=example_user_id,
            github_username=example_username,
            build_number=example_build_number,
            fingerprint=example_fingerprint
        )

        # 2. Validate the newly created session
        print("\n--- Step 2: Validating the session ---")
        is_valid = validate_session(db=db_client, session_id=session_id)
        print(f"Validation result for session {session_id}: {'Valid' if is_valid else 'Invalid'}")

        # 3. Example of validating a non-existent session
        print("\n--- Step 3: Validating a non-existent session ---")
        validate_session(db=db_client, session_id="non-existent-session-id")

    else:
        print("\nCould not run demonstration because Firebase initialization failed.")
        print("Please ensure you have set up your service account key correctly.")