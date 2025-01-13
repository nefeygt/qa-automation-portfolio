import pytest
from utils.api_client import GitHubAPIClient
import json

class TestGitHubAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_client = GitHubAPIClient()

    @pytest.mark.parametrize("search_query", [
        "python",
        "selenium",
        "javascript",
        "react"
    ])
    def test_search_repositories(self, search_query):
        """Test the GitHub repository search API with various queries"""
        response = self.api_client.search_repositories(search_query)
        
        # Verify successful response
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        
        # Verify response structure
        data = response.json()
        assert "items" in data, "Response should contain 'items' field"
        
        # Verify search results
        repos = data["items"]
        assert len(repos) > 0, f"No repositories found for query: {search_query}"
        
        # Verify repository fields
        first_repo = repos[0]
        required_fields = ["id", "name", "full_name", "html_url", "description"]
        for field in required_fields:
            assert field in first_repo, f"Repository should have {field} field"

    def test_repository_sorting(self):
        """Test repository search with different sorting options"""
        # Get repositories sorted by stars
        response_stars = self.api_client.search_repositories("python", sort="stars")
        stars_data = response_stars.json()
        
        # Verify sorting by stars
        repos_stars = stars_data["items"][:2]  # Get top 2 repos
        assert repos_stars[0]["stargazers_count"] >= repos_stars[1]["stargazers_count"], \
            "Repositories should be sorted by stars in descending order"

    def test_invalid_search(self):
        """Test search API with invalid query parameters"""
        response = self.api_client.search_repositories("" * 500)  # Very long empty query
        assert response.status_code != 200, "Should not return 200 for invalid query"

    def test_rate_limiting(self):
        """Test API rate limiting headers"""
        response = self.api_client.search_repositories("test")
        assert "X-RateLimit-Limit" in response.headers, "Rate limit headers should be present"
        assert "X-RateLimit-Remaining" in response.headers, "Rate limit remaining header should be present"