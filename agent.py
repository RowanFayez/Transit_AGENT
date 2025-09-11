"""
Alexandria Transit AI Agent - Main Entry Point
Smart transit assistant with MCP integration for OpenTripPlanner
"""

import asyncio
import os
from dotenv import load_dotenv
from transit_agent import transit_agent

# Load environment variables
load_dotenv()

async def interactive_mode():
    """Interactive command-line interface"""
    print("🚌 Alexandria Transit AI Agent")
    print("=" * 50)
    print("Type your query in Arabic or English")
    print("Examples:")
    print("  - أريد الذهاب من المنتزه إلى فيكتوريا")
    print("  - How do I go from Montazah to Sidi Gaber?")
    print("  - من سيدي جابر إلى الرمل")
    print("  - Route from Victoria to Raml Station")
    print("\nType 'quit' to exit, 'status' to check system status")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🚌 Query: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == 'status':
                status = await transit_agent.check_system_status()
                print(f"\n📊 System Status:")
                print(f"   OTP Server: {status['otp_status']['status']}")
                print(f"   Available Stops: {status['geocoder_stops']}")
                print(f"   Memory System: {'✅ Loaded' if status['memory_loaded'] else '❌ Error'}")
                continue
            
            if not user_input:
                continue
            
            print("\n🤔 Processing...")
            response = await transit_agent.process_query(user_input)
            print(f"\n🤖 Response:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

async def main():
    """Main function"""
    # Check if OTP is running
    status = await transit_agent.check_system_status()
    
    if status['otp_status']['status'] != 'online':
        print("⚠️  Warning: OTP server is not running!")
        print("Please start your OTP instance at http://localhost:8080")
        print("The agent will still work for location geocoding but won't provide routes.")
        print()
    
    # Start interactive mode
    await interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())