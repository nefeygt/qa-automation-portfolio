import requests
from utils.config_reader import read_config
import time

class GitHubAPIClient:
    def __init__(self):
        self.config = read_config()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.config['github']['token']}"
        }

    def _handle_rate_limit(self, response):
        """Handle rate limiting"""
        if response.status_code == 403:
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = reset_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    return True
        return False

    def search_repositories(self, query, params=None):
        """
        Search for GitHub repositories with optional parameters and rate limit handling
        """
        endpoint = f"{self.base_url}/search/repositories"
        search_params = {
            "q": query,
        }
        if params:
            search_params.update(params)
        
        response = requests.get(endpoint, headers=self.headers, params=search_params)
        
        # Handle rate limiting
        if self._handle_rate_limit(response):
            # Retry the request if we hit the rate limit
            response = requests.get(endpoint, headers=self.headers, params=search_params)
        
        return response
    
    def get_repository(self, owner, repo):
        """
        Get details of a specific repository
        Args:
            owner (str): Repository owner's username
            repo (str): Repository name
        Returns:
            response: API response containing repository details
        """
        endpoint = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(endpoint, headers=self.headers)
        
        # Handle rate limiting
        if self._handle_rate_limit(response):
            # Retry the request if we hit the rate limit
            response = requests.get(endpoint, headers=self.headers)
        
        return response