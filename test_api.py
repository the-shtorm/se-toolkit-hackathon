"""Comprehensive API test script for Smart Notification Manager."""
import requests
import sys
import time
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000"
API = f"{BASE_URL}/api/v1"

# Test results tracking
passed = 0
failed = 0
errors = []

def test(name, func):
    global passed, failed
    try:
        func()
        passed += 1
        print(f"  ✅ {name}")
    except AssertionError as e:
        failed += 1
        errors.append(f"❌ {name}: {e}")
        print(f"  ❌ {name}: {e}")
    except Exception as e:
        failed += 1
        errors.append(f"❌ {name}: {e}")
        print(f"  ❌ {name}: {type(e).__name__}: {e}")

# ============================================================
# V1: AUTHENTICATION
# ============================================================
print("\n🔐 V1: AUTHENTICATION")

auth_headers = {}
user_id = None

def test_register():
    r = requests.post(f"{API}/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPass123!"
    })
    assert r.status_code in (201, 409), f"Expected 201/409, got {r.status_code}: {r.text}"
    # 409 is OK if user already exists from previous run

def test_login():
    global auth_headers
    r = requests.post(f"{API}/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    # Extract cookies
    auth_headers = {"Cookie": "; ".join([f"{c.name}={c.value}" for c in r.cookies])}

def test_me():
    global user_id
    r = requests.get(f"{API}/auth/me", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    user_id = data["id"]
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

test("Register user", test_register)
test("Login user", test_login)
test("Get current user (/me)", test_me)

# ============================================================
# V1: NOTIFICATIONS
# ============================================================
print("\n🔔 V1: NOTIFICATIONS")

notif_id = None

def test_create_notification():
    global notif_id
    r = requests.post(f"{API}/notifications", headers=auth_headers, json={
        "title": "Test Notification",
        "message": "This is a test notification",
        "priority": "high"
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    notif_id = data["id"]
    assert data["title"] == "Test Notification"
    assert data["priority"] == "high"

def test_list_notifications():
    r = requests.get(f"{API}/notifications", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) > 0

def test_get_notification():
    r = requests.get(f"{API}/notifications/{notif_id}", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["id"] == notif_id

def test_mark_as_read():
    r = requests.put(f"{API}/notifications/{notif_id}/read", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["status"] == "read" or data["read_at"] is not None

def test_mark_all_as_read():
    r = requests.put(f"{API}/notifications/read-all", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "count" in data or "message" in data

test("Create notification", test_create_notification)
test("List notifications", test_list_notifications)
test("Get notification", test_get_notification)
test("Mark as read", test_mark_as_read)
test("Mark all as read", test_mark_all_as_read)

# ============================================================
# V1: WEBSOCKET (basic connectivity)
# ============================================================
print("\n🔌 V1: WEBSOCKET")

def test_websocket_endpoint():
    import websocket
    try:
        ws = websocket.create_connection(f"ws://localhost:8000/ws/notifications")
        ws.close()
        assert True
    except Exception as e:
        # WebSocket endpoint may require auth (403) or return 400 for HTTP request
        # Both are acceptable - just verifying the route exists
        r = requests.get(f"{BASE_URL}/ws/notifications", headers={"Upgrade": "websocket", "Connection": "Upgrade"})
        assert r.status_code in (400, 403, 426, 101), f"Expected WS endpoint behavior, got {r.status_code}"

test("WebSocket endpoint exists", test_websocket_endpoint)

# ============================================================
# V2: GROUPS
# ============================================================
print("\n👥 V2: GROUPS")

group_id = None
user2_id = None

def test_create_group():
    global group_id
    r = requests.post(f"{API}/groups", headers=auth_headers, json={
        "name": "Test Group",
        "description": "A test group for notifications"
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    group_id = data["id"]
    assert data["name"] == "Test Group"

def test_list_groups():
    r = requests.get(f"{API}/groups", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "items" in data

def test_add_member_to_group():
    global user2_id
    # Create second user first
    r = requests.post(f"{API}/auth/register", json={
        "email": "user2@example.com",
        "username": "user2",
        "password": "User2Pass123!"
    })
    # user2 may already exist (409 is ok)

    # Get user2 id from users list
    r = requests.get(f"{API}/users", headers=auth_headers, params={"page": 1, "page_size": 50})
    if r.status_code == 200:
        users_data = r.json()
        # Handle both list and dict response formats
        user_list = users_data if isinstance(users_data, list) else users_data.get("items", [])
        for u in user_list:
            if u["username"] == "user2":
                user2_id = u["id"]
                break

    if user2_id:
        r = requests.post(f"{API}/groups/{group_id}/members", headers=auth_headers, json={
            "user_id": user2_id,
            "role": "member"
        })
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"

def test_get_group():
    r = requests.get(f"{API}/groups/{group_id}", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["id"] == group_id

def test_update_group():
    r = requests.put(f"{API}/groups/{group_id}", headers=auth_headers, json={
        "name": "Updated Test Group",
        "description": "Updated description"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["name"] == "Updated Test Group"

def test_delete_group():
    global group_id
    r = requests.delete(f"{API}/groups/{group_id}", headers=auth_headers)
    assert r.status_code == 204, f"Expected 204, got {r.status_code}: {r.text}"
    # Verify deletion
    r = requests.get(f"{API}/groups/{group_id}", headers=auth_headers)
    assert r.status_code == 404, f"Expected 404 after delete, got {r.status_code}"

test("Create group", test_create_group)
test("List groups", test_list_groups)
test("Add member to group", test_add_member_to_group)
test("Get group", test_get_group)
test("Update group", test_update_group)
test("Delete group", test_delete_group)

# ============================================================
# V2: EVENTS
# ============================================================
print("\n📅 V2: EVENTS")

event_id = None

def test_create_event():
    global event_id
    future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r = requests.post(f"{API}/events", headers=auth_headers, json={
        "name": "Scheduled Event",
        "title": "Event Notification",
        "message": "This is a scheduled event notification",
        "priority": "medium",
        "scheduled_at": future_time
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    event_id = data["id"]
    assert data["name"] == "Scheduled Event"
    assert data["celery_task_id"] is not None

def test_list_events():
    r = requests.get(f"{API}/events", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "items" in data
    assert "total" in data

def test_get_event():
    r = requests.get(f"{API}/events/{event_id}", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["id"] == event_id

def test_update_event():
    r = requests.put(f"{API}/events/{event_id}", headers=auth_headers, json={
        "name": "Updated Event",
        "title": "Updated Title",
        "message": "Updated message"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["name"] == "Updated Event"

def test_delete_event():
    r = requests.delete(f"{API}/events/{event_id}", headers=auth_headers)
    assert r.status_code == 204, f"Expected 204, got {r.status_code}: {r.text}"

test("Create event", test_create_event)
test("List events", test_list_events)
test("Get event", test_get_event)
test("Update event", test_update_event)
test("Delete event", test_delete_event)

# ============================================================
# V2: TEMPLATES
# ============================================================
print("\n📝 V2: TEMPLATES")

template_id = None

def test_create_template():
    global template_id
    r = requests.post(f"{API}/templates", headers=auth_headers, json={
        "name": "Meeting Reminder",
        "title_template": "Reminder: {meeting_name}",
        "message_template": "Don't forget about {meeting_name} at {time}",
        "priority": "medium",
        "category": "meeting",
        "is_public": True
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    template_id = data["id"]
    assert data["name"] == "Meeting Reminder"
    assert data["is_public"] is True

def test_list_templates():
    r = requests.get(f"{API}/templates", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "items" in data
    assert "total" in data

def test_get_template():
    r = requests.get(f"{API}/templates/{template_id}", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["id"] == template_id

def test_update_template():
    r = requests.put(f"{API}/templates/{template_id}", headers=auth_headers, json={
        "name": "Updated Meeting Reminder",
        "priority": "high"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["name"] == "Updated Meeting Reminder"

def test_delete_template():
    r = requests.delete(f"{API}/templates/{template_id}", headers=auth_headers)
    assert r.status_code == 204, f"Expected 204, got {r.status_code}: {r.text}"

test("Create template", test_create_template)
test("List templates", test_list_templates)
test("Get template", test_get_template)
test("Update template", test_update_template)
test("Delete template", test_delete_template)

# ============================================================
# V2: PREFERENCES
# ============================================================
print("\n⚙️ V2: PREFERENCES")

def test_get_preferences():
    r = requests.get(f"{API}/preferences", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "user_id" in data
    assert "web_enabled" in data

def test_create_preferences():
    r = requests.post(f"{API}/preferences", headers=auth_headers, json={
        "web_enabled": True,
        "email_enabled": False,
        "sms_enabled": False,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "max_daily_notifications": 30,
        "timezone": "US/Pacific",
        "digest_enabled": True,
        "digest_frequency": "daily"
    })
    # May be 409 if already exists from auto-creation
    assert r.status_code in (201, 409), f"Expected 201/409, got {r.status_code}: {r.text}"

def test_update_preferences():
    r = requests.put(f"{API}/preferences", headers=auth_headers, json={
        "web_enabled": True,
        "email_enabled": True,
        "sms_enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "08:00",
        "max_daily_notifications": 25,
        "timezone": "Europe/London",
        "digest_enabled": False,
        "digest_frequency": "weekly"
    })
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["web_enabled"] is True
    assert data["timezone"] == "Europe/London"
    assert data["digest_enabled"] is False

test("Get preferences", test_get_preferences)
test("Create preferences", test_create_preferences)
test("Update preferences", test_update_preferences)

# ============================================================
# V2: SNOOZE
# ============================================================
print("\n⏰ V2: SNOOZE")

# Create a notification to snooze
snooze_notif_id = None

def test_setup_snooze():
    global snooze_notif_id
    r = requests.post(f"{API}/notifications", headers=auth_headers, json={
        "title": "Snooze Test",
        "message": "Testing snooze functionality",
        "priority": "low"
    })
    assert r.status_code == 201
    snooze_notif_id = r.json()["id"]

def test_snooze_notification():
    snooze_until = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r = requests.post(f"{API}/snoozes", headers=auth_headers, json={
        "notification_id": snooze_notif_id,
        "snoozed_until": snooze_until
    })
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["notification_id"] == snooze_notif_id

def test_quick_snooze():
    r = requests.post(f"{API}/snoozes/quick?notification_id={snooze_notif_id}&duration=1h", headers=auth_headers)
    assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["notification_id"] == snooze_notif_id

def test_list_snoozes():
    r = requests.get(f"{API}/snoozes", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert isinstance(data, list)

def test_snooze_options():
    r = requests.get(f"{API}/snoozes/options", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "options" in data
    assert len(data["options"]) > 0

def test_unsnooze():
    r = requests.delete(f"{API}/snoozes/{snooze_notif_id}", headers=auth_headers)
    assert r.status_code == 204, f"Expected 204, got {r.status_code}: {r.text}"

test("Setup snooze notification", test_setup_snooze)
test("Snooze notification", test_snooze_notification)
test("Quick snooze", test_quick_snooze)
test("List snoozes", test_list_snoozes)
test("Get snooze options", test_snooze_options)
test("Un-snooze notification", test_unsnooze)

# ============================================================
# V2: ANALYTICS / STATS
# ============================================================
print("\n📊 V2: ANALYTICS")

def test_stats_endpoint():
    r = requests.get(f"{API}/notifications/stats", headers=auth_headers)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "unread_count" in data
    assert "total" in data
    assert "read_rate" in data
    assert "by_priority" in data
    assert "daily_last_7_days" in data
    print(f"    📈 Stats: total={data['total']}, read_rate={data['read_rate']}%")

test("Stats endpoint", test_stats_endpoint)

# ============================================================
# V2: PRODUCTION SERVICES
# ============================================================
print("\n🚀 V2: PRODUCTION SERVICES")

def test_nginx_health():
    r = requests.get("http://localhost/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["status"] == "healthy"

def test_nginx_api_proxy():
    r = requests.get("http://localhost/api/v1/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

def test_backend_direct():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

def test_redis_connection():
    # Verify via celery worker is running
    import subprocess
    result = subprocess.run(
        ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.v2.yml", "ps", "--format", "json"],
        capture_output=True, text=True
    )
    assert "celery-worker" in result.stdout or "celery-beat" in result.stdout

test("Nginx health", test_nginx_health)
test("Nginx API proxy", test_nginx_api_proxy)
test("Backend direct", test_backend_direct)
test("Redis/Celery services", test_redis_connection)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print(f"📋 TEST SUMMARY")
print("="*60)
print(f"  ✅ Passed: {passed}")
print(f"  ❌ Failed: {failed}")
print(f"  📊 Total:  {passed + failed}")
print("="*60)

if failed > 0:
    print("\n❌ FAILED TESTS:")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
else:
    print("\n🎉 ALL TESTS PASSED!")
    sys.exit(0)
