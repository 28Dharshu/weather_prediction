"""
Verification test suite for python_app
"""
import sys
from app import app

def run_tests():
    client = app.test_client()
    passed = 0
    total = 0

    def assert_eq(actual, expected, desc):
        nonlocal passed, total
        total += 1
        if actual == expected:
            passed += 1
            print(f"  [PASS] {desc}")
        else:
            print(f"  [FAIL] {desc} (Got: {actual}, Expected: {expected})")

    print("\n--- 1. Testing Page Routes ---")
    res = client.get("/login")
    assert_eq(res.status_code, 200, "GET /login returns 200")
    assert_eq("Sign In" in res.get_data(as_text=True), True, "/login contains 'Sign In'")

    res = client.get("/register")
    assert_eq(res.status_code, 200, "GET /register returns 200")
    assert_eq("Create Account" in res.get_data(as_text=True), True, "/register contains 'Create Account'")

    # Unauthorized access should redirect to /login
    res = client.get("/dashboard")
    assert_eq(res.status_code, 302, "GET /dashboard redirects when unauthenticated")

    print("\n--- 2. Testing Authentication APIs ---")
    # Test valid login with seeded demo account
    res = client.post("/api/auth/login", json={"username": "demo", "password": "demo123"})
    assert_eq(res.status_code, 200, "POST /api/auth/login returns 200")
    data = res.get_json()
    assert_eq(data.get("success"), True, "Login response success is True")

    # Now client is authenticated in session
    res = client.get("/dashboard")
    assert_eq(res.status_code, 200, "GET /dashboard returns 200 after login")

    res = client.get("/api/auth/me")
    assert_eq(res.status_code, 200, "GET /api/auth/me returns 200")
    user_data = res.get_json()
    assert_eq(user_data.get("user", {}).get("username"), "demo", "Current user is 'demo'")

    print("\n--- 3. Testing Posts and Social APIs ---")
    res = client.get("/api/posts")
    assert_eq(res.status_code, 200, "GET /api/posts returns 200")
    posts = res.get_json().get("posts", [])
    assert_eq(len(posts) > 0, True, "Posts count > 0")

    post_id = posts[0]["id"]
    # Toggle like
    res = client.post(f"/api/posts/{post_id}/like")
    assert_eq(res.status_code, 200, f"POST /api/posts/{post_id}/like returns 200")
    assert_eq(res.get_json().get("liked"), True, "Post liked successfully")

    # Add comment
    res = client.post(f"/api/posts/{post_id}/comments", json={"comment_text": "Automated test comment!"})
    assert_eq(res.status_code, 201, f"POST /api/posts/{post_id}/comments returns 201")

    # Get comments
    res = client.get(f"/api/posts/{post_id}/comments")
    assert_eq(res.status_code, 200, f"GET /api/posts/{post_id}/comments returns 200")
    comments = res.get_json().get("comments", [])
    assert_eq(any("Automated test comment!" in c.get("comment", "") for c in comments), True, "New comment found")

    print("\n--- 4. Testing Profile and Gallery Pages ---")
    res = client.get("/profile")
    assert_eq(res.status_code, 200, "GET /profile returns 200")

    res = client.get("/gallery")
    assert_eq(res.status_code, 200, "GET /gallery returns 200")

    res = client.get("/api/profile")
    assert_eq(res.status_code, 200, "GET /api/profile returns 200")

    print(f"\n==========================================")
    print(f"Results: {passed} / {total} tests passed!")
    print(f"==========================================\n")
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
