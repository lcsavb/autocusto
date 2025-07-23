#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autocusto.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create admin user
admin = User.objects.create_user('test@test.com', 'test123')
admin.is_staff = True
admin.save()

# Get dashboard content
client = Client()
client.force_login(admin)
response = client.get('/analytics/')
content = response.content.decode('utf-8')

print(f"Response status: {response.status_code}")
print(f"Content length: {len(content)}")

# Check for Chart.js CDN
if 'chart.js' in content:
    print("✅ Chart.js CDN found")
else:
    print("❌ Chart.js CDN missing")

# Extract JavaScript content
js_start = content.find('<script>')
js_end = content.rfind('</script>')

if js_start != -1 and js_end != -1:
    js_content = content[js_start:js_end + 9]
    print("\n=== JAVASCRIPT CONTENT ===")
    print(js_content)
    print("=== END JAVASCRIPT ===")
    print(f"JavaScript length: {len(js_content)}")
else:
    print("❌ No JavaScript section found")

# Check for template extends
if 'extends "base.html"' in content:
    print("✅ Template extends base.html")
else:
    print("❌ Template not extending base.html")

# Look for specific missing elements
missing_elements = [
    'loadDailyTrends',
    'Chart.js',
    'DOMContentLoaded',
    'analytics:api_daily_trends'
]

print("\n=== MISSING ELEMENTS CHECK ===")
for element in missing_elements:
    if element in content:
        print(f"✅ {element}: Found")
    else:
        print(f"❌ {element}: Missing")