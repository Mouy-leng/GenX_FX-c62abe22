import sys
import os
import logging

# Add the project root to the Python path to allow for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from services.litewriter_client import LiteWriterClient
from services.github_service import GitHubService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_note_for_tasks(note_content: str, note_title: str) -> list:
    """
    Parses the content of a note to find tasks.
    Tasks are identified by lines starting with "TODO:", "- [ ]", or "TASK:".

    Args:
        note_content: The full text of the note.
        note_title: The title of the note, used for context in the issue body.

    Returns:
        A list of dictionaries, where each dictionary represents a task
        with a 'title' and 'body'.
    """
    tasks = []
    lines = note_content.split('\n')
    for line in lines:
        line_stripped = line.strip()
        task_title = None

        if line_stripped.upper().startswith("TODO:"):
            task_title = line_stripped[5:].strip()
        elif line_stripped.upper().startswith("TASK:"):
            task_title = line_stripped[5:].strip()
        elif line_stripped.startswith("- [ ]"):
            task_title = line_stripped[5:].strip()

        if task_title:
            tasks.append({
                "title": task_title,
                "body": f"This task was generated from the note titled **'{note_title}'**.\n\n---\n\n*This issue was created automatically from a LiteWriter note.*"
            })
    return tasks

def main():
    """
    Main function to sync notes from LiteWriter to GitHub issues.
    """
    logger.info("Starting LiteWriter to GitHub sync process...")

    # Initialize services
    litewriter_client = LiteWriterClient()
    github_service = GitHubService()

    # Check if clients are operational
    if not litewriter_client.client:
        logger.error("LiteWriter client failed to initialize. Aborting sync.")
        return
    if not github_service.github_token:
        logger.error("GitHub service is not configured (missing token). Aborting sync.")
        return

    # Fetch notes
    notes = litewriter_client.list_notes()
    if not notes:
        logger.info("No notes found in LiteWriter. Sync process complete.")
        return

    logger.info(f"Found {len(notes)} notes to process.")

    total_issues_created = 0
    for note_path in notes:
        note_title = os.path.basename(note_path)
        logger.info(f"Processing note: {note_title}")

        content = litewriter_client.get_note_content(note_path)
        if not content:
            logger.warning(f"Could not retrieve content for note '{note_title}'. Skipping.")
            continue

        # Parse for tasks and create issues
        tasks = parse_note_for_tasks(content, note_title)
        if not tasks:
            logger.info(f"No actionable tasks found in '{note_title}'.")
            continue

        logger.info(f"Found {len(tasks)} tasks in '{note_title}'.")
        for task in tasks:
            success = github_service.create_issue(title=task['title'], body=task['body'])
            if success:
                total_issues_created += 1
            else:
                logger.error(f"Failed to create issue for task: '{task['title']}'")

    logger.info(f"Sync process finished. Created {total_issues_created} new GitHub issues.")

if __name__ == "__main__":
    # For this script to run, the following environment variables must be set:
    # - LITEWRITER_WEBDAV_URL
    # - LITEWRITER_USERNAME
    # - LITEWRITER_PASSWORD
    # - GITHUB_TOKEN
    # - GITHUB_REPO_OWNER (optional, defaults to Mouy-leng)
    # - GITHUB_REPO_NAME (optional, defaults to GenX_FX)
    main()