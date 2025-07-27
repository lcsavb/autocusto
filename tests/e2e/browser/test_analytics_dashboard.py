"""
Analytics Dashboard Tests using Playwright
Tests the analytics dashboard functionality including charts and API endpoints
"""

import asyncio
from playwright.async_api import async_playwright, expect
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model
from analytics.models import PDFGenerationLog, UserActivityLog, DailyMetrics
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()


class AnalyticsDashboardTest(LiveServerTestCase):
    """Test Analytics Dashboard with Playwright"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create admin user for testing
        cls.admin_user = User.objects.create_user(
            'admin@test.com', 
            'admin123'
        )
        cls.admin_user.is_staff = True
        cls.admin_user.is_superuser = True
        cls.admin_user.save()
        
        # Create test analytics data
        cls.create_test_data()
    
    @classmethod
    def create_test_data(cls):
        """Create test analytics data"""
        # Create PDF generation logs
        for i in range(10):
            PDFGenerationLog.objects.create(
                user=cls.admin_user,
                pdf_type='prescription',
                success=True,
                generation_time_ms=1000 + i * 100,
                file_size_bytes=100000 + i * 1000,
                generated_at=timezone.now() - timedelta(days=i),
                ip_address='127.0.0.1',
                user_agent='Test Browser'
            )
        
        # Create user activity logs
        for i in range(5):
            UserActivityLog.objects.create(
                user=cls.admin_user,
                activity_type='login',
                timestamp=timezone.now() - timedelta(days=i),
                ip_address='127.0.0.1',
                user_agent='Test Browser'
            )
        
        # Create daily metrics
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            DailyMetrics.objects.create(
                date=date,
                total_users=30,
                new_users=1,
                active_users=2 + i,
                total_logins=5 + i,
                failed_logins=0,
                pdfs_generated=3 + i,
                pdf_errors=0,
                total_patients=13,
                new_patients=1,
                total_processes=50,
                new_processes=2
            )
    
    def test_analytics_dashboard_loading(self):
        """Test that analytics dashboard loads correctly"""
        asyncio.run(self._test_analytics_dashboard_loading())
    
    async def _test_analytics_dashboard_loading(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                executable_path='/usr/bin/google-chrome'
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Console: {msg.text}"))
            page.on("pageerror", lambda error: print(f"Page error: {error}"))
            
            try:
                # Test API endpoints directly first
                print("Testing API endpoints directly...")
                
                # Test daily trends API
                response = await page.goto(f"{self.live_server_url}/analytics/api/daily-trends/?days=7")
                print(f"Daily trends API: {response.status}")
                
                # Test PDF analytics API
                response = await page.goto(f"{self.live_server_url}/analytics/api/pdf-analytics/?days=7")
                print(f"PDF analytics API: {response.status}")
                
                # Test healthcare insights API
                response = await page.goto(f"{self.live_server_url}/analytics/api/healthcare-insights/?days=7")
                print(f"Healthcare insights API: {response.status}")
                
                # Now test the dashboard directly (skip login for now)
                print(f"Testing dashboard at: {self.live_server_url}/analytics/")
                await page.goto(f"{self.live_server_url}/analytics/")
                await page.wait_for_load_state('networkidle')
                
                # Check if analytics dashboard loaded
                await expect(page.locator('h1')).to_contain_text('Analytics Dashboard')
                
                # Check if overview metrics are visible
                await expect(page.locator('.metric-card')).to_have_count(8)  # 4 total + 4 today
                
                # Check if time filter buttons exist
                await expect(page.locator('.btn-filter')).to_have_count(3)
                
                # Test time filter functionality
                print("Testing 30 days filter...")
                await page.click('button[data-days="30"]')
                await page.wait_for_timeout(2000)  # Wait for charts to load
                
                # Check for chart containers
                charts = ['dailyTrendsChart', 'pdfAnalyticsChart', 'healthcareChart']
                for chart in charts:
                    chart_element = page.locator(f'#{chart}')
                    await expect(chart_element).to_be_visible()
                
                # Test API endpoints directly
                print("Testing API endpoints...")
                
                # Test daily trends API
                response = await page.goto(f"{self.live_server_url}/analytics/api/daily-trends/?days=7")
                data = await response.json()
                print(f"Daily trends API response: {data}")
                
                # Test PDF analytics API
                response = await page.goto(f"{self.live_server_url}/analytics/api/pdf-analytics/?days=7")
                data = await response.json()
                print(f"PDF analytics API response: {data}")
                
                # Test healthcare insights API
                response = await page.goto(f"{self.live_server_url}/analytics/api/healthcare-insights/?days=7")
                data = await response.json()
                print(f"Healthcare insights API response: {data}")
                
                # Go back to dashboard
                await page.goto(f"{self.live_server_url}/analytics/")
                await page.wait_for_load_state('networkidle')
                
                # Wait for charts to load and check for errors
                await page.wait_for_timeout(5000)
                
                # Check if any charts are still showing loading state
                loading_elements = page.locator('.chart-loading')
                loading_count = await loading_elements.count()
                print(f"Charts still loading: {loading_count}")
                
                if loading_count > 0:
                    for i in range(loading_count):
                        loading_text = await loading_elements.nth(i).text_content()
                        print(f"Loading element {i}: {loading_text}")
                
                # Take screenshot for debugging
                await page.screenshot(path=f"{self.live_server_url.replace('http://', '').replace(':', '_')}_analytics_dashboard.png")
                
            except Exception as e:
                print(f"Test error: {e}")
                await page.screenshot(path="analytics_dashboard_error.png")
                raise
            finally:
                await browser.close()
    
    def test_api_endpoints_directly(self):
        """Test API endpoints directly without browser"""
        from django.test.client import Client
        
        client = Client()
        client.force_login(self.admin_user)
        
        # Test daily trends API
        response = client.get('/analytics/api/daily-trends/?days=7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Daily trends API data: {data}")
        
        # Test PDF analytics API
        response = client.get('/analytics/api/pdf-analytics/?days=7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"PDF analytics API data: {data}")
        
        # Test healthcare insights API
        response = client.get('/analytics/api/healthcare-insights/?days=7')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Healthcare insights API data: {data}")