import pytest
from pages.home_page import HomePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@pytest.mark.usefixtures("driver")
class TestSearch:
    @pytest.mark.parametrize("search_query", [
        "Python programming",
        "Selenium automation",
        "QA testing",
        "#technology"
    ])
    def test_search_functionality(self, driver, search_query):
        """Test the search functionality with different queries"""
        try:
            home_page = HomePage(driver)
            home_page.navigate()
            
            # Add a small wait after navigation
            time.sleep(2)
            
            home_page.search(search_query)
            
            # Wait for search results
            wait = WebDriverWait(driver, 15)
            
            # Wait for any of these elements that might indicate search results
            search_results_locators = [
                (By.CSS_SELECTOR, '[data-testid="cellInnerDiv"]'),
                (By.CSS_SELECTOR, '[data-testid="tweet"]'),
                (By.CSS_SELECTOR, '[data-testid="tweetText"]'),
                (By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            ]
            
            found = False
            for locator in search_results_locators:
                try:
                    result = wait.until(
                        EC.presence_of_element_located(locator)
                    )
                    if result.is_displayed():
                        found = True
                        break
                except:
                    continue
            
            assert found, f"No search results found for query: {search_query}"
            
            # Add a screenshot for verification
            screenshot_name = f"search_results_{search_query.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(f"reports/screenshots/{screenshot_name}")
            
        except Exception as e:
            # Take screenshot on failure
            screenshot_name = f"error_{search_query.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(f"reports/screenshots/{screenshot_name}")
            pytest.fail(f"Test failed for search query '{search_query}': {str(e)}")