"""
Test script for Alexandria Transit AI Agent
"""

import asyncio
from transit_agent import transit_agent

async def test_geocoding():
    """Test geocoding functionality"""
    print("🧪 Testing Geocoding...")
    
    test_locations = [
        "منتزه",
        "فيكتوريا", 
        "sidi gaber",
        "raml station",
        "montazah"
    ]
    
    for location in test_locations:
        result = geocoder.geocode(location)
        if result:
            lat, lon, name = result
            print(f"✅ {location} → {name} ({lat}, {lon})")
        else:
            print(f"❌ {location} → Not found")

async def test_route_planning():
    """Test route planning functionality"""
    print("\n🧪 Testing Route Planning...")
    
    test_routes = [
        ("منتزه", "فيكتوريا"),
        ("montazah", "victoria"),
        ("sidi gaber", "raml station")
    ]
    
    for from_loc, to_loc in test_routes:
        print(f"\n📍 Testing: {from_loc} → {to_loc}")
        result = await transit_agent.plan_route(from_loc, to_loc)
        
        if result["success"]:
            routes = result.get("routes", [])
            print(f"✅ Found {len(routes)} route(s)")
            for i, route in enumerate(routes[:2], 1):  # Show first 2 routes
                print(f"   Route {i}: {route['total_duration']} min, {route['transfers']} transfers")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

async def test_language_detection():
    """Test language detection"""
    print("\n🧪 Testing Language Detection...")
    
    test_queries = [
        "أريد الذهاب من المنتزه إلى فيكتوريا",
        "How do I go from Montazah to Victoria?",
        "من سيدي جابر إلى الرمل",
        "Route from Sidi Gaber to Raml Station"
    ]
    
    for query in test_queries:
        language = transit_agent.detect_language(query)
        print(f"✅ '{query[:30]}...' → {language.upper()}")

async def test_memory_system():
    """Test memory system"""
    print("\n🧪 Testing Memory System...")
    
    # Test adding recent locations
    memory_manager.add_recent_location("Test Location 1", 31.2, 29.9)
    memory_manager.add_recent_location("Test Location 2", 31.3, 29.8)
    
    recent = memory_manager.get_recent_locations(3)
    print(f"✅ Recent locations: {len(recent)}")
    
    # Test preferences
    prefs = memory_manager.get_preferences()
    print(f"✅ User preferences loaded: {prefs.language}")

async def main():
    """Run all tests"""
    print("🚌 Alexandria Transit AI Agent - Test Suite")
    print("=" * 50)
    
    # Test individual components
    await test_geocoding()
    await test_language_detection()
    await test_memory_system()
    
    # Test route planning (only if OTP is available)
    print("\n🧪 Testing OTP Connection...")
    status = await transit_agent.check_system_status()
    if status['otp_status']['status'] == 'online':
        await test_route_planning()
    else:
        print("⚠️  OTP server not available - skipping route planning tests")
        print(f"   OTP Status: {status['otp_status']['status']}")
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main())
