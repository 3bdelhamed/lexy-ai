"""Simple test to verify API endpoints work"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health endpoint works!")

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing / endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Root endpoint works!")

def test_simplify_modes():
    """Test get simplification modes"""
    print("\n🔍 Testing /simplify/modes endpoint...")
    response = requests.get(f"{BASE_URL}/simplify/modes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Available modes: {data.get('modes', [])}")
    assert response.status_code == 200
    print("✅ Modes endpoint works!")

def test_tts_voices():
    """Test get TTS voices"""
    print("\n🔍 Testing /tts/voices endpoint...")
    response = requests.get(f"{BASE_URL}/tts/voices")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Available voices: {data.get('voices', [])}")
    assert response.status_code == 200
    print("✅ Voices endpoint works!")

def test_simplify_text_short():
    """Test text simplification with short text"""
    print("\n🔍 Testing /simplify/text endpoint (short text)...")
    payload = {
        "text": "The quick brown fox jumps over the lazy dog.",
        "mode": "general",
        "intensity": "medium"
    }
    response = requests.post(f"{BASE_URL}/simplify/text", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Original: {data.get('original_text', '')[:50]}...")
        print(f"Simplified: {data.get('simplified_text', '')[:50]}...")
        print(f"Processing time: {data.get('processing_time_ms', 0):.2f}ms")
        print("✅ Text simplification works!")
    else:
        print(f"❌ Error: {response.text}")
        print("⚠️  Make sure you have set GEMINI_API_KEY in .env file")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Lexy-AI API Endpoint Tests")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        test_simplify_modes()
        test_tts_voices()
        test_simplify_text_short()
        
        print("\n" + "=" * 60)
        print("✅ All basic tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server")
        print("Make sure the server is running: python src/main.py")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
