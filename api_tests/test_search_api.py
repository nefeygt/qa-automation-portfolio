import pytest
from utils.api_client import TwitterAPIClient
import json

class TestTwitterAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api_client = TwitterAPIClient()

    @pytest.mark.parametrize("search_query", [
        "Python programming",
        "Selenium automation",
        "QA testing",
        "#technology"
    ])
    def test_search_tweets(self, search_query):
        """Test the Twitter search API with various queries"""
        response = self.api_client.search_tweets(search_query)
        
        # Verify successful response
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
        
        # Verify response structure
        data = response.json()
        assert "data" in data, "Response should contain 'data' field"
        
        # Verify search results
        tweets = data["data"]
        assert len(tweets) > 0, f"No tweets found for query: {search_query}"
        
        # Verify tweet fields
        for tweet in tweets:
            assert "id" in tweet, "Tweet should have an ID"
            assert "text" in tweet, "Tweet should have text content"
            
    def test_search_with_invalid_query(self):
        """Test search API with invalid query parameters"""
        response = self.api_client.search_tweets("" * 500)  # Very long empty query
        assert response.status_code == 400, "Should return 400 for invalid query"

    def test_search_rate_limits(self):
        """Test API rate limiting headers"""
        response = self.api_client.search_tweets("test")
        assert "x-rate-limit-remaining" in response.headers, "Rate limit headers should be present"