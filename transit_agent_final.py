#!/usr/bin/env python3
"""
Final Alexandria Transit AI Agent with proper OTP integration and fixes
"""

import asyncio
import re
import os
import json
import aiohttp
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv
from geocoding_full import AlexandriaGeocoder

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

@dataclass
class Route:
    duration: int  # in minutes
    distance: float  # in kilometers
    steps: List[Dict[str, Any]]
    total_walking_time: int
    transit_modes: List[str]

class FinalTransitAgent:
    """Final Alexandria Transit AI Agent with all fixes"""
    
    def __init__(self):
        self.geocoder = AlexandriaGeocoder()
        self.model = genai.GenerativeModel('gemini-pro')
        self.otp_url = "http://localhost:8080"
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Arabic/Egyptian or English"""
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "en"
        
        arabic_ratio = arabic_chars / total_chars
        return "ar" if arabic_ratio > 0.3 else "en"
    
    def normalize_egyptian_text(self, text: str) -> str:
        """Normalize Egyptian Arabic text for better matching"""
        egyptian_patterns = {
            'عايز': 'أريد', 'عايزة': 'أريد', 'عاوز': 'أريد', 'عاوزة': 'أريد',
            'روح': 'اذهب', 'روحة': 'اذهب', 'روحه': 'اذهب',
            'إزاي': 'كيف', 'ازاي': 'كيف', 'إمتى': 'متى',
            'منين': 'من أين', 'فين': 'أين', 'ليه': 'لماذا',
            'المنشية': 'المنشية', 'منشية': 'المنشية',
            'السيوف': 'السيوف', 'سيوف': 'السيوف', 'سيف': 'السيوف'
        }
        
        normalized_text = text
        for egyptian, standard in egyptian_patterns.items():
            normalized_text = normalized_text.replace(egyptian, standard)
        
        return normalized_text
    
    def extract_locations(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract from and to locations from query with enhanced Arabic support"""
        # Normalize Egyptian Arabic
        normalized_query = self.normalize_egyptian_text(query)
        query_lower = normalized_query.lower()
        
        # Enhanced patterns for Egyptian Arabic and English
        patterns = [
            # Standard Arabic patterns
            r'أريد\s+الذهاب\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'كيف\s+أصل\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'من\s+(.+?)\s+إلى\s+(.+)',
            r'من\s+(.+?)\s+لـ\s*(.+)',
            
            # Egyptian Arabic patterns
            r'عايز\s+أروح\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'عايزة\s+أروح\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'عاوز\s+أروح\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'عاوزة\s+أروح\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'إزاي\s+أروح\s+من\s+(.+?)\s+إلى\s+(.+)',
            r'ازاي\s+أروح\s+من\s+(.+?)\s+لـ\s*(.+)',
            
            # English patterns
            r'how\s+do\s+i\s+go\s+from\s+(.+?)\s+to\s+(.+)',
            r'route\s+from\s+(.+?)\s+to\s+(.+)',
            r'from\s+(.+?)\s+to\s+(.+)',
            r'i\s+want\s+to\s+go\s+from\s+(.+?)\s+to\s+(.+)',
            r'travel\s+from\s+(.+?)\s+to\s+(.+)',
            
            # Simple patterns for specific destinations
            r'من\s+(.+?)\s+لفيكتوريا',
            r'من\s+(.+?)\s+للمنتزه',
            r'من\s+(.+?)\s+لسيدي\s+جابر',
            r'من\s+(.+?)\s+للرمل',
            r'من\s+(.+?)\s+للفلكي',
            r'من\s+(.+?)\s+لسيدي\s+بشر',
            r'من\s+(.+?)\s+لجليم',
            r'من\s+(.+?)\s+للسبورتنج',
            r'من\s+(.+?)\s+لسموحة',
            r'من\s+(.+?)\s+لكرموز',
            r'من\s+(.+?)\s+للسيوف',
            r'من\s+(.+?)\s+للمنشية'
        ]
        
        for pattern in patterns:
            try:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match and len(match.groups()) >= 2:
                    from_loc = match.group(1).strip()
                    to_loc = match.group(2).strip()
                    return from_loc, to_loc
                elif match and len(match.groups()) >= 1:
                    from_loc = match.group(1).strip()
                    # Extract destination from pattern
                    destination_map = {
                        'لفيكتوريا': 'فيكتوريا',
                        'للمنتزه': 'المنتزه',
                        'لسيدي جابر': 'سيدي جابر',
                        'للرمل': 'الرمل',
                        'للفلكي': 'الفلكي',
                        'لسيدي بشر': 'سيدي بشر',
                        'لجليم': 'جليم',
                        'للسبورتنج': 'السبورتنج',
                        'لسموحة': 'سموحة',
                        'لكرموز': 'كرموز',
                        'للسيوف': 'السيوف',
                        'للمنشية': 'المنشية'
                    }
                    
                    for key, value in destination_map.items():
                        if key in pattern:
                            return from_loc, value
            except Exception:
                continue
        
        # Try to find location mentions using fuzzy matching
        location_mentions = []
        for stop in self.geocoder.get_all_stops():
            for alias in stop.aliases:
                if alias.lower() in query_lower:
                    location_mentions.append((alias, stop))
        
        if len(location_mentions) >= 2:
            return location_mentions[0][0], location_mentions[1][0]
        
        return None, None
    
    async def geocode_location(self, location_name: str) -> Optional[Tuple[float, float, str]]:
        """Geocode a location name to coordinates"""
        result = self.geocoder.geocode(location_name)
        if result:
            return result
        
        # If not found, try with search
        matches = self.geocoder.search_stops(location_name)
        if matches:
            stop = matches[0]  # Take the first match
            return stop.stop_lat, stop.stop_lon, stop.stop_name
        
        return None
    
    async def check_otp_status(self) -> bool:
        """Check if OTP server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.otp_url}/otp/routers/default", timeout=5) as response:
                    return response.status == 200
        except:
            return False
    
    async def plan_route_with_otp(self, from_coords: Tuple[float, float], to_coords: Tuple[float, float]) -> Optional[Route]:
        """Plan route using OpenTripPlanner with proper time calculation"""
        try:
            # Check OTP status first
            if not await self.check_otp_status():
                print("OTP server is not running")
                return None
            
            url = f"{self.otp_url}/otp/routers/default/plan"
            params = {
                'fromPlace': f"{from_coords[0]},{from_coords[1]}",
                'toPlace': f"{to_coords[0]},{to_coords[1]}",
                'mode': 'TRANSIT,WALK',
                'maxWalkDistance': 2000,
                'arriveBy': 'false',
                'numItineraries': 3
            }
            
            print(f"Requesting OTP route from {from_coords} to {to_coords}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=15) as response:
                    print(f"OTP Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'plan' in data and 'itineraries' in data['plan'] and len(data['plan']['itineraries']) > 0:
                            itinerary = data['plan']['itineraries'][0]  # Take first route
                            
                            steps = []
                            transit_modes = []
                            total_walking_time = 0
                            
                            for leg in itinerary['legs']:
                                mode = leg['mode']
                                duration_minutes = leg['duration'] // 1000 // 60  # Convert to minutes
                                
                                if mode == 'WALK':
                                    total_walking_time += duration_minutes
                                
                                step = {
                                    'mode': mode,
                                    'from': leg['from']['name'],
                                    'to': leg['to']['name'],
                                    'duration': duration_minutes,
                                    'distance': leg['distance'] / 1000  # Convert to km
                                }
                                steps.append(step)
                                
                                if mode != 'WALK':
                                    transit_modes.append(mode)
                            
                            # Calculate total duration properly
                            total_duration = itinerary['duration'] // 1000 // 60
                            
                            return Route(
                                duration=total_duration,
                                distance=sum(leg['distance'] for leg in itinerary['legs']) / 1000,
                                steps=steps,
                                total_walking_time=total_walking_time,
                                transit_modes=list(set(transit_modes))
                            )
                        else:
                            print("No itineraries found in OTP response")
                            return None
                    else:
                        print(f"OTP request failed with status {response.status}")
                        return None
        except Exception as e:
            print(f"OTP Error: {e}")
            return None
    
    def format_route_response(self, route: Route, from_name: str, to_name: str, language: str) -> str:
        """Format route response in the appropriate language with proper names"""
        if language == "ar":
            response = f"""
🚌 **خطة الرحلة من {from_name} إلى {to_name}**

⏱️ **الوقت الكلي:** {route.duration} دقيقة
📏 **المسافة الكلية:** {route.distance:.1f} كم
🚶 **وقت المشي:** {route.total_walking_time} دقيقة

**تفاصيل الرحلة:**
"""
            
            for i, step in enumerate(route.steps, 1):
                if step['mode'] == 'WALK':
                    response += f"{i}. 🚶 امشي من **{step['from']}** إلى **{step['to']}** ({step['duration']} دق - {step['distance']:.1f} كم)\n"
                else:
                    mode_name = {
                        'BUS': 'أتوبيس',
                        'TRAM': 'ترام',
                        'RAIL': 'قطار',
                        'SUBWAY': 'مترو'
                    }.get(step['mode'], step['mode'])
                    response += f"{i}. 🚌 اركب {mode_name} من **{step['from']}** إلى **{step['to']}** ({step['duration']} دق)\n"
            
            if route.transit_modes:
                response += f"\n**وسائل النقل المستخدمة:** {', '.join(route.transit_modes)}"
            
        else:
            response = f"""
🚌 **Trip Plan from {from_name} to {to_name}**

⏱️ **Total Time:** {route.duration} minutes
📏 **Total Distance:** {route.distance:.1f} km
🚶 **Walking Time:** {route.total_walking_time} minutes

**Trip Details:**
"""
            
            for i, step in enumerate(route.steps, 1):
                if step['mode'] == 'WALK':
                    response += f"{i}. 🚶 Walk from **{step['from']}** to **{step['to']}** ({step['duration']} min - {step['distance']:.1f} km)\n"
                else:
                    response += f"{i}. 🚌 Take {step['mode']} from **{step['from']}** to **{step['to']}** ({step['duration']} min)\n"
            
            if route.transit_modes:
                response += f"\n**Transit Modes Used:** {', '.join(route.transit_modes)}"
        
        return response
    
    def create_basic_route(self, from_coords: Tuple[float, float, str], to_coords: Tuple[float, float, str], language: str) -> str:
        """Create a basic route when OTP is not available"""
        if language == "ar":
            return f"""
🚌 **خطة الرحلة من {from_coords[2]} إلى {to_coords[2]}**

📍 **من:** {from_coords[2]} ({from_coords[0]:.4f}, {from_coords[1]:.4f})
📍 **إلى:** {to_coords[2]} ({to_coords[0]:.4f}, {to_coords[1]:.4f})

**الخيارات المتاحة:**
1. **أتوبيس:** استخدم شبكة الأتوبيسات العامة
2. **ترام:** استخدم ترام الإسكندرية (إذا كان متاحاً في المنطقة)
3. **ميكروباص:** وسيلة نقل سريعة ومرنة
4. **تاكسي:** للراحة والسرعة

📱 **نصائح:**
- استخدم تطبيق المواصلات الرسمي للمواعيد الدقيقة
- تحقق من مواعيد التشغيل قبل السفر
- احتفظ بخيارات بديلة للطوارئ

⚠️ **ملاحظة:** هذه معلومات أساسية. لتفاصيل الطرق الدقيقة والمواعيد، يرجى التأكد من تشغيل خادم OTP المحلي.
"""
        else:
            return f"""
🚌 **Trip Plan from {from_coords[2]} to {to_coords[2]}**

📍 **From:** {from_coords[2]} ({from_coords[0]:.4f}, {from_coords[1]:.4f})
📍 **To:** {to_coords[2]} ({to_coords[0]:.4f}, {to_coords[1]:.4f})

**Available Options:**
1. **Bus:** Use the public bus network
2. **Tram:** Use Alexandria tram system (if available in the area)
3. **Microbus:** Fast and flexible transport option
4. **Taxi:** For comfort and speed

📱 **Tips:**
- Use the official transport app for accurate schedules
- Check operating hours before traveling
- Keep backup options for emergencies

⚠️ **Note:** This is basic information. For detailed routes and schedules, please ensure your local OTP server is running.
"""
    
    async def process_query(self, user_query: str) -> str:
        """Process user query and return response"""
        try:
            # Detect language
            language = self.detect_language(user_query)
            
            # Extract locations
            from_location, to_location = self.extract_locations(user_query)
            
            if not from_location or not to_location:
                if language == "ar":
                    return "من فضلك حدد نقطة البداية والوجهة بوضوح. مثال: 'عايز أروح من الفلكي لسيدي جابر' أو 'من فيكتوريا إلى المنتزه'"
                else:
                    return "Please specify both starting point and destination clearly. Example: 'I want to go from Falaki to Sidi Gaber' or 'from Victoria to Montazah'"
            
            # Geocode locations
            from_coords = await self.geocode_location(from_location)
            to_coords = await self.geocode_location(to_location)
            
            if not from_coords:
                if language == "ar":
                    return f"عذراً، لم أتمكن من العثور على موقع: **{from_location}**. تأكد من كتابة الاسم بطريقة صحيحة."
                else:
                    return f"Sorry, I couldn't find the location: **{from_location}**. Please check the spelling."
            
            if not to_coords:
                if language == "ar":
                    return f"عذراً، لم أتمكن من العثور على موقع: **{to_location}**. تأكد من كتابة الاسم بطريقة صحيحة."
                else:
                    return f"Sorry, I couldn't find the location: **{to_location}**. Please check the spelling."
            
            # Try to plan route with OTP
            route = await self.plan_route_with_otp((from_coords[0], from_coords[1]), (to_coords[0], to_coords[1]))
            
            if route:
                return self.format_route_response(route, from_coords[2], to_coords[2], language)
            else:
                # Fallback to basic route info
                return self.create_basic_route(from_coords, to_coords, language)
                
        except Exception as e:
            if self.detect_language(user_query) == "ar":
                return f"عذراً، حدث خطأ في معالجة طلبك: {str(e)}"
            else:
                return f"Sorry, an error occurred while processing your request: {str(e)}"

# Create global instance
transit_agent = FinalTransitAgent()

async def main():
    """Test the final agent"""
    print("🚌 Alexandria Transit AI Agent - Final Version")
    print("=" * 70)
    
    # Check OTP status
    otp_status = await transit_agent.check_otp_status()
    print(f"OTP Status: {'✅ Running' if otp_status else '❌ Not Running'}")
    
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
        print(f"\n🔍 Query: {query}")
        response = await transit_agent.process_query(query)
        print(f"🤖 Response: {response}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
