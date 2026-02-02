"""
Container utilities for Playwright testing in Docker environments.
Provides process monitoring, cleanup, and debugging tools.
"""
import subprocess
import psutil
import os
import signal
from pathlib import Path


class ContainerProcessManager:
    """Manage Chrome processes in container environments."""
    
    @staticmethod
    def cleanup_chrome_processes():
        """Clean up any defunct or orphaned Chrome processes."""
        try:
            # Kill any existing Chrome processes
            subprocess.run(['pkill', '-f', 'chrome'], capture_output=True)
            subprocess.run(['pkill', '-f', 'chromium'], capture_output=True)
            
            # Wait a moment for processes to terminate
            import time
            time.sleep(2)
            
            print("✅ Chrome processes cleaned up")
            return True
        except Exception as e:
            print(f"⚠️ Chrome cleanup failed: {e}")
            return False
    
    @staticmethod
    def get_chrome_process_count():
        """Get count of Chrome processes including zombies."""
        try:
            result = subprocess.run(
                ['ps', 'aux'], 
                capture_output=True, 
                text=True
            )
            
            lines = result.stdout.split('\n')
            chrome_processes = [line for line in lines if 'chrome' in line.lower()]
            zombie_count = len([line for line in chrome_processes if '<defunct>' in line])
            active_count = len(chrome_processes) - zombie_count
            
            return {
                'total': len(chrome_processes),
                'active': active_count,
                'zombie': zombie_count
            }
        except Exception as e:
            print(f"⚠️ Failed to get process count: {e}")
            return {'total': 0, 'active': 0, 'zombie': 0}
    
    @staticmethod
    def monitor_resources():
        """Monitor container resource usage."""
        try:
            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = None
            mem_available = None
            for line in meminfo.split('\n'):
                if 'MemTotal:' in line:
                    mem_total = int(line.split()[1])  # in kB
                elif 'MemAvailable:' in line:
                    mem_available = int(line.split()[1])  # in kB
            
            if mem_total and mem_available:
                mem_used_percent = ((mem_total - mem_available) / mem_total) * 100
                
                print(f"🖥️  Memory: {mem_used_percent:.1f}% used")
                
                if mem_used_percent > 85:
                    print("⚠️ High memory usage detected")
                    return False
                    
            return True
        except Exception as e:
            print(f"⚠️ Resource monitoring failed: {e}")
            return True
    
    @staticmethod
    def check_network_connectivity(url="http://127.0.0.1:8001/"):
        """Check if Django server is accessible."""
        # Skip network check when using StaticLiveServerTestCase
        # It will start its own server on a random port
        import os
        if os.environ.get('CI') and os.environ.get('DJANGO_SETTINGS_MODULE') == 'test_settings':
            print("🌐 Network check: Skipping - StaticLiveServerTestCase will start its own server")
            return True
            
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', url],
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            status_code = result.stdout.strip()
            print(f"🌐 Network check: {url} -> {status_code}")
            
            # Accept 200 (OK) or 302 (Redirect) as success
            return status_code in ['200', '302']
        except Exception as e:
            print(f"🌐 Network check failed: {e}")
            return False


class PlaywrightContainerDebugger:
    """Debug Playwright issues in container environments."""
    
    def __init__(self, test_instance):
        self.test = test_instance
        self.debug_dir = Path('playwright_debug')
        self.debug_dir.mkdir(exist_ok=True)
    
    def capture_debug_info(self, stage_name):
        """Capture comprehensive debug information."""
        debug_info = {
            'stage': stage_name,
            'processes': ContainerProcessManager.get_chrome_process_count(),
            'network': ContainerProcessManager.check_network_connectivity(),
            'resources_ok': ContainerProcessManager.monitor_resources()
        }
        
        # Capture page state if available
        if hasattr(self.test, 'page') and self.test.page:
            try:
                debug_info['page_url'] = self.test.page.url
                debug_info['page_title'] = self.test.page.title()
                
                # Take screenshot
                screenshot_path = self.debug_dir / f"{stage_name}_screenshot.png"
                self.test.page.screenshot(path=str(screenshot_path))
                debug_info['screenshot'] = str(screenshot_path)
                
            except Exception as e:
                debug_info['page_error'] = str(e)
        
        # Save debug info to file
        debug_file = self.debug_dir / f"{stage_name}_debug.txt"
        with open(debug_file, 'w') as f:
            for key, value in debug_info.items():
                f.write(f"{key}: {value}\n")
        
        print(f"🔍 Debug info captured: {debug_file}")
        return debug_info
    
    def health_check_before_test(self):
        """Perform health checks before running tests."""
        print("🏥 Performing container health checks...")
        
        # Clean up any leftover processes
        ContainerProcessManager.cleanup_chrome_processes()
        
        # Check resources
        if not ContainerProcessManager.monitor_resources():
            print("⚠️ Resource constraints detected")
        
        # Check network - Django runs on port 8001 in CI
        network_ok = ContainerProcessManager.check_network_connectivity("http://localhost:8001/")
        if not network_ok:
            print("⚠️ Network connectivity issues detected")
        
        # Check if we're using Playwright server approach
        playwright_server_endpoint = os.environ.get("PW_TEST_CONNECT_WS_ENDPOINT")
        if playwright_server_endpoint:
            print("✅ Using official Playwright server approach - Chrome not needed in this container")
            print(f"📡 Playwright server endpoint: {playwright_server_endpoint}")
            return True
        
        # Fallback: Check Chrome availability (for legacy setups)
        chrome_paths = [
            '/usr/bin/google-chrome-stable',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium'
        ]
        
        chrome_available = False
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_available = True
                print(f"✅ Chrome found: {path}")
                break
        
        if not chrome_available:
            print("❌ No Chrome installation found (legacy mode)")
        
        return chrome_available