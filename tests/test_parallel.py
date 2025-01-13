import pytest
from pages.home_page import HomePage
from utils.api_client import GitHubAPIClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class TestParallel:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.driver = driver
        self.api_client = GitHubAPIClient()
        self.home_page = HomePage(self.driver)

    def convert_to_k_format(self, number):
        """Convert a number to k format (e.g., 31305 to 31.3k)"""
        if number >= 1000:
            return f"{number/1000:.1f}k"
        return str(number)

    def test_repository_details_validation(self):
        """Test repository details consistency between UI and API"""
        repo_owner = "SeleniumHQ"
        repo_name = "selenium"
        
        # Get repository details via API
        api_response = self.api_client.get_repository(repo_owner, repo_name)
        assert api_response.status_code == 200
        api_data = api_response.json()
        
        # Navigate to repository page in UI
        self.driver.get(f"https://github.com/{repo_owner}/{repo_name}")
        wait = WebDriverWait(self.driver, 10)
        
        # Dictionary of metrics to check
        metrics = {
            'stars': {
                'ui_selector': '[id="repo-stars-counter-star"]',
                'api_key': 'stargazers_count'
            },
            'forks': {
                'ui_selector': '[id="repo-network-counter"]',
                'api_key': 'forks_count'
            }
        }
        
        results = []
        for metric_name, metric_data in metrics.items():
            try:
                # Wait for element and get text
                ui_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, metric_data['ui_selector']))
                )
                ui_text = ui_element.text.lower().strip()
                
                # Clean up UI value
                ui_value = ui_text.replace(',', '').split()[0]
                
                # Get API value
                api_value = api_data[metric_data['api_key']]
                api_k_value = self.convert_to_k_format(api_value).lower()
                
                # Compare values based on format
                if 'k' in ui_value:
                    assert ui_value == api_k_value, \
                        f"{metric_name} count mismatch - UI: {ui_value}, API: {api_k_value}"
                else:
                    assert int(ui_value) == api_value, \
                        f"{metric_name} count mismatch - UI: {ui_value}, API: {api_value}"
                
                # Store successful result
                results.append({
                    'metric': metric_name,
                    'ui_value': ui_value,
                    'api_value': f"{api_value:,}",
                    'status': 'PASS'
                })
                
            except Exception as e:
                print(f"\nError processing {metric_name}:")
                print(f"Error details: {str(e)}")
                results.append({
                    'metric': metric_name,
                    'error': str(e),
                    'status': 'FAIL'
                })
        
        # Take screenshot for the report
        screenshot_name = f"repo_metrics_{int(time.time())}.png"
        self.driver.save_screenshot(f"reports/screenshots/{screenshot_name}")
        
        # Print results in a readable format
        print("\nRepository Metrics Validation Results:")
        print("=====================================")
        for result in results:
            status_color = "✅" if result['status'] == 'PASS' else "❌"
            if result['status'] == 'PASS':
                print(f"{status_color} {result['metric'].title()}:")
                print(f"   UI: {result['ui_value']}")
                print(f"   API: {result['api_value']}")
                print(f"   Comparison: {'MATCH' if result['status'] == 'PASS' else 'MISMATCH'}")
            else:
                print(f"{status_color} {result['metric'].title()}: {result['error']}")
            print("-------------------------------------")
        
        # Store results for the HTML report
        self.test_data = {
            'screenshot': screenshot_name,
            'results': results,
            'repository': f"{repo_owner}/{repo_name}"
        }
        
        # Assert all metrics passed
        assert all(r['status'] == 'PASS' for r in results), "Some metrics validation failed"