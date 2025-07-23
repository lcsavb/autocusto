#!/usr/bin/env python
"""
Debug Analytics Dashboard JavaScript Issues
Tests the analytics dashboard without Playwright dependency
"""

import os
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from analytics.models import PDFGenerationLog, UserActivityLog, DailyMetrics
from django.utils import timezone
from datetime import timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

User = get_user_model()

class AnalyticsJSDebugTest(TestCase):
    """Debug JavaScript issues in analytics dashboard"""
    
    @classmethod
    def setUpTestData(cls):
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
    
    def test_dashboard_renders(self):
        """Test that dashboard renders without errors"""
        client = Client()
        client.force_login(self.admin_user)
        
        response = client.get('/analytics/')
        
        print(f"📊 Dashboard Response Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for essential elements
            checks = [
                ('Analytics Dashboard', 'H1 title present'),
                ('Chart.js CDN', 'chart.js in content'),
                ('dailyTrendsChart', 'Daily trends chart element'),
                ('pdfAnalyticsChart', 'PDF analytics chart element'),
                ('healthcareChart', 'Healthcare chart element'),
                ('loadAllCharts', 'Chart loading function'),
                ('DOMContentLoaded', 'DOM ready event listener'),
            ]
            
            for check_text, description in checks:
                if check_text in content:
                    print(f"✅ {description}: Found")
                else:
                    print(f"❌ {description}: Missing")
            
            # Check for potential issues
            issues = [
                ('console.error', 'Error logging present'),
                ('404', 'Potential 404 errors'),
                ('undefined', 'Undefined variables'),
                ('null', 'Null references'),
            ]
            
            for issue_text, description in issues:
                if issue_text in content:
                    print(f"⚠️  {description}: Found")
            
            print(f"\n📄 Template content length: {len(content)} characters")
            
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Response content: {response.content.decode('utf-8')[:500]}...")
    
    def test_api_endpoints_directly(self):
        """Test API endpoints that charts depend on"""
        client = Client()
        client.force_login(self.admin_user)
        
        endpoints = [
            ('/analytics/api/daily-trends/?days=7', 'Daily Trends'),
            ('/analytics/api/pdf-analytics/?days=7', 'PDF Analytics'),
            ('/analytics/api/healthcare-insights/?days=7', 'Healthcare Insights'),
        ]
        
        print(f"\n🔍 Testing API Endpoints:")
        
        for endpoint, name in endpoints:
            try:
                response = client.get(endpoint)
                print(f"📡 {name}: Status {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ JSON Response: {len(str(data))} chars")
                        
                        # Check for expected data structure
                        if endpoint.endswith('daily-trends/?days=7'):
                            expected_keys = ['dates', 'pdfs_generated', 'active_users', 'new_patients']
                            for key in expected_keys:
                                if key in data:
                                    print(f"   ✅ {key}: {len(data[key]) if isinstance(data[key], list) else 'present'}")
                                else:
                                    print(f"   ❌ {key}: missing")
                        
                        elif endpoint.endswith('pdf-analytics/?days=7'):
                            if 'pdf_by_type' in data:
                                print(f"   ✅ pdf_by_type: {len(data['pdf_by_type'])} items")
                            else:
                                print(f"   ❌ pdf_by_type: missing")
                        
                        elif endpoint.endswith('healthcare-insights/?days=7'):
                            if 'top_diseases' in data:
                                print(f"   ✅ top_diseases: {len(data['top_diseases'])} items")
                            else:
                                print(f"   ❌ top_diseases: missing")
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Invalid JSON: {e}")
                        print(f"   Raw content: {response.content[:200]}...")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    print(f"   Content: {response.content[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    def test_javascript_template_structure(self):
        """Test JavaScript structure in template"""
        client = Client()
        client.force_login(self.admin_user)
        
        response = client.get('/analytics/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            print(f"\n🔍 JavaScript Structure Analysis:")
            
            # Extract JavaScript content
            js_start = content.find('<script>')
            js_end = content.rfind('</script>')
            
            if js_start != -1 and js_end != -1:
                js_content = content[js_start:js_end + 9]
                print(f"📄 JavaScript section: {len(js_content)} characters")
                
                # Check for function definitions
                functions = [
                    'loadDailyTrends',
                    'loadPdfAnalytics', 
                    'loadHealthcareInsights',
                    'loadAllCharts',
                    'setupTimeFilters'
                ]
                
                for func in functions:
                    if f'function {func}' in js_content:
                        print(f"   ✅ Function {func}: Defined")
                    else:
                        print(f"   ❌ Function {func}: Missing")
                
                # Check for potential issues
                if 'console.log' in js_content:
                    log_count = js_content.count('console.log')
                    print(f"   🔍 Debug logging: {log_count} statements")
                
                if 'console.error' in js_content:
                    error_count = js_content.count('console.error')
                    print(f"   ⚠️  Error logging: {error_count} statements")
                
                # Check URL template tags
                url_tags = [
                    '{% url "analytics:api_daily_trends" %}',
                    '{% url "analytics:api_pdf_analytics" %}',
                    '{% url "analytics:api_healthcare_insights" %}'
                ]
                
                for tag in url_tags:
                    if tag in js_content:
                        print(f"   ✅ URL template tag: {tag}")
                    else:
                        print(f"   ❌ URL template tag missing: {tag}")
                
            else:
                print(f"   ❌ No JavaScript section found")

if __name__ == '__main__':
    # Run the debug test
    import unittest
    
    suite = unittest.TestLoader().loadTestsFromTestCase(AnalyticsJSDebugTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n🎯 DEBUG SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES:")
        for test, error in result.failures:
            print(f"  {test}: {error}")
    
    if result.errors:
        print(f"\n❌ ERRORS:")
        for test, error in result.errors:
            print(f"  {test}: {error}")