import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self.db = self._initialize_firebase()

    def _initialize_firebase(self):
        """
        Initializes the Firebase Admin SDK.

        Credentials should be set in the environment via GOOGLE_APPLICATION_CREDENTIALS
        pointing to the service account JSON file.
        """
        try:
            # Check if the app is already initialized
            if not firebase_admin._apps:
                # The SDK will automatically pick up the GOOGLE_APPLICATION_CREDENTIALS
                # environment variable.
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': os.getenv("FIREBASE_PROJECT_ID"),
                })
                logger.info("Firebase Admin SDK initialized successfully.")

            return firestore.client()
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            logger.error("Please ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.")
            return None

    async def create_device_session(self, user_id: str, device_id: str, expires_in_hours: int = 24) -> str:
        """
        Creates a new session for a user and their device in Firestore.

        Args:
            user_id: The unique identifier for the user (e.g., from GitHub).
            device_id: The verified device build number.
            expires_in_hours: How long the session is valid for.

        Returns:
            The ID of the created session document.
        """
        if not self.db:
            raise ConnectionError("Firestore client not initialized.")

        expiration_time = datetime.utcnow() + timedelta(hours=expires_in_hours)

        session_data = {
            "userId": user_id,
            "deviceId": device_id,
            "createdAt": datetime.utcnow(),
            "expiresAt": expiration_time,
            "status": "active"
        }

        try:
            doc_ref = self.db.collection('deviceSessions').add(session_data)
            logger.info(f"Created new device session for user {user_id} with ID {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Failed to create device session for user {user_id}: {e}")
            return None

    async def verify_device_session(self, session_id: str) -> bool:
        """
        Verifies if a given session ID is active and not expired.

        Args:
            session_id: The ID of the session to verify.

        Returns:
            True if the session is valid, False otherwise.
        """
        if not self.db:
            raise ConnectionError("Firestore client not initialized.")

        try:
            session_ref = self.db.collection('deviceSessions').document(session_id)
            session_doc = session_ref.get()

            if not session_doc.exists:
                logger.warning(f"Session verification failed: Session ID {session_id} not found.")
                return False

            session_data = session_doc.to_dict()
            if session_data['status'] != 'active':
                logger.warning(f"Session verification failed: Session {session_id} is not active.")
                return False

            if datetime.utcnow() > session_data['expiresAt']:
                logger.warning(f"Session verification failed: Session {session_id} has expired.")
                # Optionally, update the status to 'expired'
                # session_ref.update({"status": "expired"})
                return False

            logger.info(f"Successfully verified session {session_id}.")
            return True
        except Exception as e:
            logger.error(f"Error verifying session {session_id}: {e}")
            return False

# Example of how to instantiate the service
# firebase_service = FirebaseService()