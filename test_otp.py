#!/usr/bin/env python3
"""
Test OTP integration
"""

import asyncio
import aiohttp
import json

async def test_otp_connection():
    """Test OTP connection and routing"""
    print("🧪 Testing OTP Connection...")
    print("=" * 50)
    
    # Test OTP server status
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/otp/routers/default", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ OTP Server is running!")
                    print(f"   Router ID: {data.get('routerId', 'N/A')}")
                    print(f"   Transit Modes: {data.get('transitModes', [])}")
                    print(f"   Center: {data.get('centerLatitude', 'N/A')}, {data.get('centerLongitude', 'N/A')}")
                else:
                    print(f"❌ OTP Server returned status: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ OTP Server connection failed: {e}")
        return False
    
    # Test route planning
    print("\n🚌 Testing Route Planning...")
    print("-" * 30)
    
    # Test coordinates (Victoria to Sidi Gaber)
    from_coords = (31.248845, 29.980624)  # Victoria Station
    to_coords = (31.218117, 29.941997)    # Sidi Gaber Station
    
    try:
        url = "http://localhost:8080/otp/routers/default/plan"
        params = {
            'fromPlace': f"{from_coords[0]},{from_coords[1]}",
            'toPlace': f"{to_coords[0]},{to_coords[1]}",
            'mode': 'TRANSIT,WALK',
            'maxWalkDistance': 2000,
            'arriveBy': 'false',
            'numItineraries': 3
        }
        
        print(f"Requesting route from {from_coords} to {to_coords}")
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=15) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Route planning successful!")
                    
                    if 'plan' in data and 'itineraries' in data['plan']:
                        itineraries = data['plan']['itineraries']
                        print(f"   Found {len(itineraries)} route options")
                        
                        for i, itinerary in enumerate(itineraries[:2]):  # Show first 2 routes
                            print(f"\n   Route {i+1}:")
                            print(f"   - Duration: {itinerary['duration'] // 1000 // 60} minutes")
                            print(f"   - Distance: {sum(leg['distance'] for leg in itinerary['legs']) / 1000:.1f} km")
                            print(f"   - Legs: {len(itinerary['legs'])}")
                            
                            for j, leg in enumerate(itinerary['legs'][:3]):  # Show first 3 legs
                                mode = leg['mode']
                                from_name = leg['from']['name']
                                to_name = leg['to']['name']
                                duration = leg['duration'] // 1000 // 60
                                print(f"     {j+1}. {mode}: {from_name} → {to_name} ({duration} min)")
                    else:
                        print("❌ No itineraries found in response")
                        print(f"Response: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ Route planning failed with status: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    
    except Exception as e:
        print(f"❌ Route planning error: {e}")
    
    return True

async def test_agent():
    """Test the transit agent"""
    print("\n🤖 Testing Transit Agent...")
    print("-" * 30)
    
    try:
        from transit_agent_otp import transit_agent
        
        # Test queries
        test_queries = [
            "عايز أروح من فيكتوريا لسيدي جابر",
            "من الفلكي للمنتزه",
            "I want to go from Victoria to Sidi Gaber"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            response = await transit_agent.process_query(query)
            print(f"🤖 Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Agent test error: {e}")

async def main():
    """Main test function"""
    print("🚌 Alexandria Transit OTP Test")
    print("=" * 50)
    
    # Test OTP connection
    otp_ok = await test_otp_connection()
    
    if otp_ok:
        # Test agent
        await test_agent()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
