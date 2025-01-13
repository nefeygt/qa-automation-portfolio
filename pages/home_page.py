from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from utils.config_reader import read_config
import time

class HomePage(BasePage):
    # Element locators
    SEARCH_INPUT = (By.CSS_SELECTOR, '[data-testid="SearchBox_Search_Input"]')
    LOGIN_USERNAME = (By.NAME, "text")
    LOGIN_PASSWORD = (By.NAME, "password")
    
    def navigate(self):
        config = read_config()
        self.driver.get("https://twitter.com/login")
        
        # Login process with proper waits
        self.wait.until(EC.presence_of_element_located(self.LOGIN_USERNAME))
        username_input = self.driver.find_element(*self.LOGIN_USERNAME)
        username_input.send_keys(config['credentials']['username'])
        username_input.send_keys(Keys.RETURN)
        
        self.wait.until(EC.presence_of_element_located(self.LOGIN_PASSWORD))
        password_input = self.driver.find_element(*self.LOGIN_PASSWORD)
        password_input.send_keys(config['credentials']['password'])
        password_input.send_keys(Keys.RETURN)
        
        # Wait for search box to be available
        self.wait.until(EC.presence_of_element_located(self.SEARCH_INPUT))
    
    def search(self, query):
        try:
            # Wait for search box and click it
            search_box = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
            search_box.click()
            
            # Clear it (just in case)
            search_box.clear()
            
            # Type the query slowly
            for char in query:
                search_box.send_keys(char)
                time.sleep(0.1)  # Small delay between characters
                
            # Wait a moment before pressing Enter
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN)
            
            # Wait after search
            time.sleep(2)
        except Exception as e:
            raise Exception(f"Failed to perform search: {str(e)}")