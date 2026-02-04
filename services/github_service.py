import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "Mouy-leng")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "GenX_FX")
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"

        if not self.github_token:
            logger.warning("GITHUB_TOKEN environment variable not set. GitHubService will not be able to authenticate.")

    def create_issue(self, title: str, body: str) -> bool:
        """
        Creates a new issue in the GitHub repository.

        Args:
            title: The title of the issue.
            body: The content of the issue.

        Returns:
            True if the issue was created successfully, False otherwise.
        """
        if not self.github_token:
            logger.error("Cannot create GitHub issue: GITHUB_TOKEN is not configured.")
            return False

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        payload = {
            "title": title,
            "body": body,
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            issue_data = response.json()
            logger.info(f"Successfully created GitHub issue #{issue_data['number']}: '{title}'")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create GitHub issue. Status code: {e.response.status_code if e.response else 'N/A'}")
            logger.error(f"Response body: {e.response.text if e.response else 'N/A'}")
            return False