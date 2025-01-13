import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def pytest_html_report_title(report):
    report.title = "UI and API Parallel Test Report"

@pytest.fixture(scope="function")
def driver(request):
    # Setup
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    yield driver
    
    # Take screenshot if test fails (more reliable way)
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_name = f"fail_{request.node.name}_{timestamp}.png"
        driver.save_screenshot(f"reports/screenshots/{screenshot_name}")
    
    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        if hasattr(item, "funcargs"):
            test_instance = item.funcargs.get("self")
            if test_instance and hasattr(test_instance, "test_data"):
                data = test_instance.test_data
                report.extra = []
                
                # Add screenshot
                if 'screenshot' in data:
                    report.extra.append(("Screenshot", data['screenshot']))
                
                # Add repository info
                if 'repository' in data:
                    report.extra.append(("Repository", data['repository']))
                
                # Add detailed results
                if 'results' in data:
                    for result in data['results']:
                        if result['status'] == 'PASS':
                            report.extra.append((
                                f"{result['metric'].title()} Validation",
                                f"UI: {result['ui_value']} | API: {result['api_value']}"
                            ))
                        else:
                            report.extra.append((
                                f"{result['metric'].title()} Validation",
                                f"Failed: {result['error']}"
                            ))