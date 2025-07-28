"""
Pytest configuration for Playwright testsdf
"""
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
if not settings.configured:
    django.setup()

import pytest
from playwright.sync_api import sync_playwright
from django.test import LiveServerTestCase
from django.test.utils import override_settings


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for the test session"""
    with sync_playwright() as p:
        # Use system Chrome with Docker-optimized configuration
        browser = p.chromium.launch(
            headless=True,
            executable_path='/usr/bin/google-chrome-stable',
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--single-process',
                '--disable-setuid-sandbox',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--window-size=1920,1080'
            ],
            timeout=30000  # 30 second timeout
        )
        
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test"""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True,
        java_script_enabled=True
    )
    page = context.new_page()
    
    # Set aggressive timeouts to prevent hanging
    page.set_default_timeout(15000)  # 15 seconds
    page.set_default_navigation_timeout(15000)  # 15 seconds
    
    yield page
    context.close()


@pytest.fixture(scope="session")
def live_server():
    """Create a live Django server for Playwright tests"""
    from django.test.testcases import LiveServerThread
    from django.core.management import call_command
    import threading
    import socket
    
    # Find available port
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    # Create server thread
    server_thread = LiveServerThread('127.0.0.1', port, connections_override={})
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    import time
    time.sleep(2)
    
    # Create mock object with url attribute
    class MockServer:
        def __init__(self, host, port):
            self.url = f"http://{host}:{port}"
    
    mock_server = MockServer('127.0.0.1', port)
    
    yield mock_server
    
    # Cleanup
    server_thread.terminate()
    server_thread.join()