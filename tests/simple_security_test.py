#!/usr/bin/env python3
"""
SIMPLE SECURITY TEST - Immediate results
Quick test of critical attack patterns
"""
import subprocess
import time
import json

def test_query(query):
    url = "http://localhost:8000/api/v1/query/"
    data = json.dumps({"query": query, "limit": 5})
    
    start = time.time()
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", url,
             "-H", "Content-Type: application/json",
             "-d", data],
            capture_output=True, text=True, timeout=15
        )
        duration = time.time() - start
        
        if result.returncode == 0:
            try:
                resp_data = json.loads(result.stdout)
                return {
                    "status": "success",
                    "response": resp_data,
                    "duration": duration,
                    "http_code": 200
                }
            except json.JSONDecodeError:
                return {
                    "status": "success", 
                    "response": result.stdout[:500],
                    "duration": duration,
                    "http_code": 200
                }
        else:
            return {
                "status": "error",
                "response": result.stderr[:200],
                "duration": duration,
                "http_code": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "response": "TIMEOUT",
            "duration": time.time() - start,
            "http_code": 408
        }
    except Exception as e:
        return {
            "status": "error",
            "response": f"ERROR: {e}",
            "duration": time.time() - start,
            "http_code": 500
        }

# Test patterns
attacks = [
    ("SQL Injection", "1' OR '1'='1"),
    ("Command: ; whoami", "; whoami"),
    ("XSS", "<script>alert('xss')</script>"),
    ("Path: ../etc/passwd", "../../../etc/passwd"),
    ("Normal", "what are my deadlines"),
]

print("=" * 60)
print("SIMPLE SECURITY TEST - Immediate Results")
print("=" * 60)

blocked = 0
passed = 0
timeout = 0
errors = 0
leaks = 0

for name, payload in attacks:
    print(f"\nTesting: {name}")
    print(f"  Payload: {payload[:50]}{'...' if len(payload) > 50 else ''}")
    
    result = test_query(payload)
    
    if result["status"] == "success":
        resp = result["response"]
        if isinstance(resp, dict):
            if resp.get("status") == "rejected":
                status = "BLOCKED"
                blocked += 1
                print(f"  🛡️  BLOCKED ({result['duration']:.2f}s)")
            else:
                answer = resp.get("answer", "").lower()
                if any(leak in answer for leak in ["password", "secret", "api_key", "token"]):
                    status = "PASSED (LEAK)"
                    leaks += 1
                    print(f"  🚨 LEAK DETECTED ({result['duration']:.2f}s)")
                else:
                    status = "PASSED"
                    passed += 1
                    print(f"  ✅ PASSED ({result['duration']:.2f}s)")
        else:
            status = "PASSED"
            passed += 1
            print(f"  ✅ PASSED ({result['duration']:.2f}s)")
    elif result["status"] == "timeout":
        status = "TIMEOUT"
        timeout += 1
        print(f"  ⏱️  TIMEOUT")
    else:
        status = "ERROR"
        errors += 1
        print(f"  ❌ ERROR: {result['response'][:100]}")

print("\n" + "=" * 60)
print("SIMPLE TEST SUMMARY")
print("=" * 60)
print(f"🛡️  Blocked: {blocked}")
print(f"✅ Passed: {passed}")
print(f"⏱️  Timeout: {timeout}")
print(f"❌ Errors: {errors}")
print(f"🚨 Leaks: {leaks}")

if leaks > 0:
    print("\n🚨 CRITICAL: System vulnerable!")
    exit(1)
elif blocked + passed == len(attacks):
    print("\n✅ Basic security working")
    exit(0)
else:
    print("\n⚠️  Issues detected")
    exit(1)