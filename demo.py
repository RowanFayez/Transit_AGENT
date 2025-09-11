"""
Demo script for Alexandria Transit AI Agent
Shows all features and capabilities
"""

import asyncio
from transit_agent import transit_agent

async def demo_geocoding():
    """Demonstrate geocoding capabilities"""
    print("🗺️  Geocoding Demo")
    print("-" * 30)
    
    locations = [
        "منتزه", "فيكتوريا", "سيدي جابر", "الرمل", "منشية",
        "montazah", "victoria", "sidi gaber", "raml", "mansheya"
    ]
    
    for location in locations:
        result = geocoder.geocode(location)
        if result:
            lat, lon, name = result
            print(f"✅ {location:15} → {name:25} ({lat:.4f}, {lon:.4f})")
        else:
            print(f"❌ {location:15} → Not found")

async def demo_language_detection():
    """Demonstrate language detection"""
    print("\n🌐 Language Detection Demo")
    print("-" * 30)
    
    queries = [
        "أريد الذهاب من المنتزه إلى فيكتوريا",
        "How do I go from Montazah to Victoria?",
        "من سيدي جابر إلى الرمل",
        "Route from Sidi Gaber to Raml Station",
        "كيف أصل من فيكتوريا إلى سيدي بشر؟",
        "I want to travel from Victoria to Sidi Bishr"
    ]
    
    for query in queries:
        language = transit_agent.detect_language(query)
        print(f"✅ {language.upper():2} | {query}")

async def demo_route_planning():
    """Demonstrate route planning"""
    print("\n🚌 Route Planning Demo")
    print("-" * 30)
    
    routes = [
        ("منتزه", "فيكتوريا", "Arabic query"),
        ("montazah", "victoria", "English query"),
        ("سيدي جابر", "الرمل", "Arabic query"),
        ("sidi gaber", "raml station", "English query")
    ]
    
    for from_loc, to_loc, description in routes:
        print(f"\n📍 {description}: {from_loc} → {to_loc}")
        print("   " + "="*50)
        
        result = await transit_agent.plan_route(from_loc, to_loc)
        
        if result["success"]:
            routes_found = result.get("routes", [])
            print(f"   ✅ Found {len(routes_found)} route(s)")
            
            for i, route in enumerate(routes_found[:2], 1):  # Show first 2 routes
                print(f"   Route {i}:")
                print(f"     ⏱️  Duration: {route['total_duration']} minutes")
                print(f"     🚶 Walking: {route['total_walking_time']} minutes")
                print(f"     🔄 Transfers: {route['transfers']}")
                print(f"     📍 Summary: {route['summary']}")
        else:
            print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

async def demo_memory_system():
    """Demonstrate memory system"""
    print("\n🧠 Memory System Demo")
    print("-" * 30)
    
    # Add some test locations
    memory_manager.add_recent_location("Test Montazah", 31.282523, 30.020785)
    memory_manager.add_recent_location("Test Victoria", 31.248845, 29.980624)
    memory_manager.add_recent_location("Test Sidi Gaber", 31.218117, 29.941997)
    
    # Show recent locations
    recent = memory_manager.get_recent_locations(5)
    print(f"✅ Recent locations ({len(recent)}):")
    for i, loc in enumerate(recent, 1):
        print(f"   {i}. {loc.name} (used {loc.usage_count} times)")
    
    # Show preferences
    prefs = memory_manager.get_preferences()
    print(f"\n✅ User preferences:")
    print(f"   Language: {prefs.language}")
    print(f"   Preferred modes: {', '.join(prefs.preferred_transit_modes)}")
    print(f"   Max walking: {prefs.max_walking_distance}m")
    print(f"   Max transfers: {prefs.max_transfers}")

async def demo_full_queries():
    """Demonstrate full query processing"""
    print("\n🤖 Full Query Processing Demo")
    print("-" * 30)
    
    queries = [
        "أريد الذهاب من المنتزه إلى فيكتوريا",
        "How do I go from Montazah to Sidi Gaber?",
        "من سيدي جابر إلى الرمل",
        "Route from Victoria to Raml Station"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("   " + "="*60)
        
        response = await transit_agent.process_query(query)
        print(f"🤖 Response:\n{response}")

async def demo_system_status():
    """Demonstrate system status checking"""
    print("\n📊 System Status Demo")
    print("-" * 30)
    
    status = await transit_agent.check_system_status()
    
    print(f"✅ OTP Server: {status['otp_status']['status']}")
    if status['otp_status']['status'] == 'online':
        print("   🟢 OpenTripPlanner is running and accessible")
    else:
        print("   🔴 OpenTripPlanner is not available")
        print(f"   Error: {status['otp_status'].get('message', 'Unknown error')}")
    
    print(f"✅ Geocoder: {status['geocoder_stops']} stops loaded")
    print(f"✅ Memory: {'Loaded' if status['memory_loaded'] else 'Error'}")

async def main():
    """Run all demos"""
    print("🚌 Alexandria Transit AI Agent - Complete Demo")
    print("=" * 60)
    
    # Run all demos
    await demo_system_status()
    await demo_geocoding()
    await demo_language_detection()
    await demo_memory_system()
    
    # Only run route planning if OTP is available
    status = await transit_agent.check_system_status()
    if status['otp_status']['status'] == 'online':
        await demo_route_planning()
        await demo_full_queries()
    else:
        print("\n⚠️  Skipping route planning demos - OTP server not available")
        print("   Start your OTP instance to see full functionality")
    
    print("\n" + "=" * 60)
    print("🎉 Demo completed!")
    print("\nTo use the agent interactively, run:")
    print("   python agent.py")
    print("\nOr start the web interface:")
    print("   python web_interface.py")

if __name__ == "__main__":
    asyncio.run(main())
