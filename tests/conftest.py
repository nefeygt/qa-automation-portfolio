import pytest
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def pytest_html_report_title(report):
    report.title = "Twitter Automation Test Report"

@pytest.fixture(scope="function")
def driver(request):
    # Setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    # Create screenshots directory if it doesn't exist
    if not os.path.exists('reports/screenshots'):
        os.makedirs('reports/screenshots')
    
    yield driver
    
    # Capture screenshot on test failure
    if request.node.rep_call.failed:
        screenshot_name = f"fail_{request.node.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join('reports/screenshots', screenshot_name)
        driver.save_screenshot(screenshot_path)
    
    # Teardown
    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item.funcargs["driver"], "outcome", report.outcome)
    setattr(item, "rep_" + report.when, report)