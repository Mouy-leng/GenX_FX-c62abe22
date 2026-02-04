import os
import logging
from webdav3.client import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiteWriterClient:
    def __init__(self):
        self.options = {
            'webdav_hostname': os.getenv("LITEWRITER_WEBDAV_URL"),
            'webdav_login':    os.getenv("LITEWRITER_USERNAME"),
            'webdav_password': os.getenv("LITEWRITER_PASSWORD")
        }
        self.client = self._connect()

    def _connect(self):
        """
        Establishes a connection to the WebDAV server.
        """
        if not all(self.options.values()):
            logger.error("LiteWriter client is not configured. Please set LITEWRITER_WEBDAV_URL, LITEWRITER_USERNAME, and LITEWRITER_PASSWORD environment variables.")
            return None
        try:
            client = Client(self.options)
            # A simple check to see if the connection is valid
            client.ls()
            logger.info("Successfully connected to LiteWriter WebDAV server.")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to LiteWriter WebDAV server: {e}")
            return None

    def list_notes(self, remote_path='/'):
        """
        Lists all files in a given remote directory.

        Args:
            remote_path: The path on the server to list files from.

        Returns:
            A list of filenames.
        """
        if not self.client:
            return []
        try:
            # We filter out directories, which end with a '/'
            files = [item['path'] for item in self.client.ls(remote_path) if not item['path'].endswith('/')]
            return files
        except Exception as e:
            logger.error(f"Failed to list notes from '{remote_path}': {e}")
            return []

    def get_note_content(self, note_path: str) -> str:
        """
        Retrieves the content of a specific note.

        Args:
            note_path: The full path to the note on the server.

        Returns:
            The content of the note as a string, or None if it fails.
        """
        if not self.client:
            return None

        # Create a temporary local path to download the file to
        local_path = os.path.join("/tmp", os.path.basename(note_path))

        try:
            # Download the file from the remote server
            self.client.download_sync(remote_path=note_path, local_path=local_path)

            # Read the content of the downloaded file
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Clean up the temporary file
            os.remove(local_path)

            return content
        except Exception as e:
            logger.error(f"Failed to get content for note '{note_path}': {e}")
            # Clean up if the download or read fails
            if os.path.exists(local_path):
                os.remove(local_path)
            return None