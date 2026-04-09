"""Test scheduled event notification delivery."""
import requests
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000"
API = f"{BASE_URL}/api/v1"

# Login
r = requests.post(f"{API}/auth/login", json={
    "email": "test@example.com",
    "password": "TestPass123!"
})
assert r.status_code == 200, f"Login failed: {r.text}"
auth_headers = {"Cookie": "; ".join([f"{c.name}={c.value}" for c in r.cookies])}
print("✅ Logged in")

# Create event scheduled for 60 seconds from now
future_time = (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat()
print(f"📅 Creating event scheduled for: {future_time}")

r = requests.post(f"{API}/events", headers=auth_headers, json={
    "name": "Test Scheduled Event",
    "title": "Scheduled Notification Test",
    "message": "This should appear in notifications when the event fires!",
    "priority": "high",
    "scheduled_at": future_time
})
assert r.status_code == 201, f"Failed to create event: {r.status_code} - {r.text}"
event = r.json()
event_id = event["id"]
notif_id = event["notification_id"]
celery_task = event["celery_task_id"]

print(f"  Event ID: {event_id}")
print(f"  Notification ID: {notif_id}")
print(f"  Celery Task ID: {celery_task}")

# Check notification status BEFORE
r = requests.get(f"{API}/notifications/{notif_id}", headers=auth_headers)
assert r.status_code == 200
notif_before = r.json()
print(f"\n📋 Notification BEFORE firing:")
print(f"  Status: {notif_before['status']}")
print(f"  Sent At: {notif_before['sent_at']}")

# Wait for the event to fire
print(f"\n⏳ Waiting 70 seconds for the event to fire...")
for i in range(70, 0, -10):
    print(f"  {i} seconds remaining...")
    time.sleep(10)

# Check notification status AFTER
r = requests.get(f"{API}/notifications/{notif_id}", headers=auth_headers)
assert r.status_code == 200
notif_after = r.json()
print(f"\n📋 Notification AFTER firing:")
print(f"  Status: {notif_after['status']}")
print(f"  Sent At: {notif_after['sent_at']}")

# List notifications
r = requests.get(f"{API}/notifications", headers=auth_headers)
assert r.status_code == 200
data = r.json()
print(f"\n📊 Total notifications: {data['total']}")

# Find our notification in the list
found = False
for n in data['items']:
    if n['id'] == notif_id:
        found = True
        print(f"✅ Found in list! Title: '{n['title']}', Status: {n['status']}")
        break

if not found:
    print(f"❌ NOT found in notification list!")

print(f"\n🎯 Summary:")
print(f"  Event created: ✅")
print(f"  Celery task scheduled: {'✅' if celery_task else '❌'}")
print(f"  Notification status changed to 'sent': {'✅' if notif_after['status'] in ('sent', 'read') else '❌'}")
print(f"  Notification visible in list: {'✅' if found else '❌'}")
