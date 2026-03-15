# Task 3: The System Agent - Implementation Plan

## query_api Tool Design

### Tool Schema
- **Name**: `query_api`
- **Description**: Send HTTP requests to the deployed backend API. Use this to get real-time data from the system.
- **Parameters**:
  - `method` (string): HTTP method (GET, POST, etc.)
  - `path` (string): API endpoint path (e.g., '/items/', '/analytics/completion-rate?lab=lab-01')
  - `body` (string, optional): JSON request body for POST requests
- **Authentication**: Uses `LMS_API_KEY` from environment in Authorization: Bearer header
- **Base URL**: Reads from `AGENT_API_BASE_URL` env var (defaults to http://localhost:42002)

### Implementation Details
```python
def query_api(method, path, body=None):
    headers = {"Authorization": f"Bearer {os.getenv('LMS_API_KEY')}"}
    if body:
        headers["Content-Type"] = "application/json"
    
    url = f"{base_url}{path}"
    response = requests.request(method, url, headers=headers, json=json.loads(body) if body else None)
    return json.dumps({"status_code": response.status_code, "body": response.text})
