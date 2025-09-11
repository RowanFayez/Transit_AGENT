#!/usr/bin/env python3
"""
Test the final transit agent
"""

import asyncio

async def test_final_agent():
    """Test the final transit agent"""
    print("🧪 Testing Final Transit Agent...")
    print("=" * 50)
    
    try:
        from transit_agent_final import transit_agent
        
        # Test queries
        test_queries = [
            "عايز أروح من الفلكي لسيدي جابر",
            "من المنشية للسيوف",
            "ازاي أروح من فيكتوريا للمنتزه",
            "من العجمي لسيدي بشر",
            "I want to go from Victoria to Sidi Gaber",
            "How do I go from Falaki to Montazah?",
            "Route from Agamy to Sidi Bishr"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: {query}")
            response = await transit_agent.process_query(query)
            print(f"🤖 Response: {response[:300]}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Test error: {e}")

async def main():
    """Main test function"""
    print("🚌 Alexandria Transit Final Test")
    print("=" * 50)
    
    await test_final_agent()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
