import os
import requests
import json
from base64 import b64encode

# --- Configuration ---
# These should be set as environment variables for security.
LITEWRITER_WEBDAV_URL = os.environ.get("LITEWRITER_WEBDAV_URL", "http://10.62.78.114:8000/webdav/")
LITEWRITER_USER = os.environ.get("LITEWRITER_USER", "genxdbxfx3@gmail.com")
LITEWRITER_PASS = os.environ.get("LITEWRITER_PASS", "Leng12345@#$01")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") # A personal access token with 'repo' scope
GITHUB_REPO = os.environ.get("GITHUB_REPO") # e.g., "your-username/your-repo"

# --- WebDAV Client Logic (Conceptual) ---
# This section demonstrates how to interact with a WebDAV server using 'requests'.
# For a more robust solution, a dedicated WebDAV library like 'webdavclient3' is recommended.

def get_webdav_auth():
    """Returns the basic authentication header for WebDAV."""
    credentials = f"{LITEWRITER_USER}:{LITEWRITER_PASS}"
    return b64encode(credentials.encode()).decode('ascii')

def get_notes_from_webdav(path="/"):
    """
    Fetches the list of files from a specific path on the WebDAV server.
    This is a simplified example; a real client would parse the XML response properly.
    """
    headers = {
        "Authorization": f"Basic {get_webdav_auth()}",
        "Depth": "1" # Get information about the directory and its immediate children
    }
    try:
        # The PROPFIND method is used to get properties (like file names) from WebDAV
        res = requests.request("PROPFIND", f"{LITEWRITER_WEBDAV_URL}{path}", headers=headers)
        res.raise_for_status()
        # In a real scenario, you'd parse the XML response to extract file names.
        # For this concept, we'll assume it returns a list of file paths.
        print(f"Successfully listed files from {path}.")
        # This is a placeholder for the parsed file list.
        # return ["/tasks/task1.md", "/tasks/task2.md"]
        return [] # Returning empty to avoid errors in a real run
    except requests.exceptions.RequestException as e:
        print(f"Error listing files from WebDAV: {e}")
        return []

def get_note_content(file_path):
    """Retrieves the content of a single note from the WebDAV server."""
    headers = {"Authorization": f"Basic {get_webdav_auth()}"}
    try:
        res = requests.get(f"{LITEWRITER_WEBDAV_URL}{file_path}", headers=headers)
        res.raise_for_status()
        print(f"Successfully fetched content for {file_path}.")
        return res.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching note content for {file_path}: {e}")
        return None

# --- GitHub API Logic ---

def create_github_issue(title, body):
    """Creates a new issue in the specified GitHub repository."""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("Error: GITHUB_TOKEN and GITHUB_REPO environment variables must be set.")
        return None

    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "title": title,
        "body": body
    }

    try:
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        res.raise_for_status()
        print(f"Successfully created GitHub issue: '{title}'")
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating GitHub issue: {e.text}")
        return None

# --- Main Automation Logic ---

def process_notes_to_issues():
    """
    Main function to fetch notes from LiteWriter and create GitHub issues.
    """
    print("Starting LiteWriter to GitHub automation process...")

    # In a real implementation, you would list files from a specific folder, e.g., "/tasks/"
    notes = get_notes_from_webdav("/tasks/") # This is conceptual

    if not notes:
        print("No notes found to process.")
        return

    for note_path in notes:
        content = get_note_content(note_path)

        if content:
            # Simple parsing: first line is the title, the rest is the body.
            lines = content.strip().split('\n')
            title = lines[0] if lines else "New Task from LiteWriter"
            body = '\n'.join(lines[1:]) if len(lines) > 1 else ""

            # Add a reference to the source note in the issue body
            body += f"\n\n---\n*Created from LiteWriter note: `{note_path}`*"

            create_github_issue(title, body)

            # In a real implementation, you would move the processed note to an archive folder
            # to prevent processing it again.
            # E.g., move_webdav_file(note_path, f"/archive/{os.path.basename(note_path)}")

    print("Automation process finished.")


if __name__ == "__main__":
    # --- Example ---
    # This is a conceptual demonstration.
    # To run this for real, you need to:
    # 1. Set the environment variables for your credentials.
    # 2. Implement a proper WebDAV client to parse the file list correctly.

    print("--- Conceptual LiteWriter-to-GitHub Automation ---")

    # A mock example of creating an issue without involving the WebDAV part.
    if GITHUB_TOKEN and GITHUB_REPO:
        print("\n--- Running a mock GitHub issue creation test ---")
        create_github_issue(
            "Test Issue from Automation Script",
            "This is a test issue to confirm that the GitHub API integration is working."
        )
    else:
        print("\nSkipping mock GitHub issue creation test.")
        print("Set GITHUB_TOKEN and GITHUB_REPO environment variables to run this test.")

    # To run the full process, you would call:
    # process_notes_to_issues()