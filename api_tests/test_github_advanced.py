import pytest
from utils.api_client import GitHubAPIClient
import json

class TestGitHubAdvanced:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_client = GitHubAPIClient()

    def test_repository_language_filter(self):
        """Test repository search with language filter"""
        query = "language:python web framework"
        response = self.api_client.search_repositories(query)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify repositories are Python-based
        for repo in data["items"][:5]:  # Check first 5 repos
            assert repo["language"].lower() == "python", \
                f"Repository {repo['full_name']} is not a Python repository"

    @pytest.mark.parametrize("stars_filter", [">1000", ">10000", ">100000"])
    def test_repository_stars_filter(self, stars_filter):
        """Test repository search with different star count filters"""
        query = f"stars:{stars_filter}"
        response = self.api_client.search_repositories(query)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify star counts meet the criteria
        min_stars = int(stars_filter[1:])
        for repo in data["items"][:5]:
            assert repo["stargazers_count"] > min_stars, \
                f"Repository {repo['full_name']} has fewer stars than expected"

    @pytest.mark.parametrize("date_range", [
        "created:>2023-01-01",
        "created:2022-01-01..2022-12-31",
        "pushed:>2023-06-01"
    ])
    def test_repository_date_filters(self, date_range):
        """Test repository search with date-based filters"""
        query = f"language:javascript {date_range}"
        response = self.api_client.search_repositories(query)
        
        assert response.status_code == 200
        assert response.json()["total_count"] > 0, \
            f"No repositories found for date range: {date_range}"

    def test_repository_topic_search(self):
        """Test searching repositories by topic"""
        query = "topic:machine-learning language:python"
        response = self.api_client.search_repositories(query)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify repositories have the specified topic
        for repo in data["items"][:5]:
            topics_response = self.api_client.get_repository(
                repo["owner"]["login"], 
                repo["name"]
            )
            repo_details = topics_response.json()
            assert "machine-learning" in repo_details.get("topics", []), \
                f"Repository {repo['full_name']} doesn't have machine-learning topic"

    def test_search_response_pagination(self):
        """Test repository search pagination"""
        per_page = 5
        query = "language:python stars:>1000"
        
        # Get first page
        first_page = self.api_client.search_repositories(
            query, 
            params={"per_page": per_page, "page": 1}
        )
        
        # Get second page
        second_page = self.api_client.search_repositories(
            query, 
            params={"per_page": per_page, "page": 2}
        )
        
        assert first_page.status_code == second_page.status_code == 200
        
        first_repos = first_page.json()["items"]
        second_repos = second_page.json()["items"]
        
        # Verify we get different results
        first_ids = [repo["id"] for repo in first_repos]
        second_ids = [repo["id"] for repo in second_repos]
        
        assert not set(first_ids).intersection(set(second_ids)), \
            "Pagination returned duplicate repositories"