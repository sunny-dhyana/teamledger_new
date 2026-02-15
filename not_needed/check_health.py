import httpx
try:
    res = httpx.get("http://localhost:8003/health")
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
except Exception as e:
    print(f"Error: {e}")
