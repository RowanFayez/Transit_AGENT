"""
MCP Server for OpenTripPlanner Integration
Handles communication with OTP instance and provides transit planning capabilities
"""

import json
import requests
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TransitRoute:
    """Represents a transit route option"""
    mode: str
    duration: int  # in minutes
    distance: float  # in meters
    legs: List[Dict[str, Any]]
    transfers: int
    walking_time: int  # in minutes

class OTPServer:
    """MCP Server for OpenTripPlanner integration"""
    
    def __init__(self, otp_base_url: str = "http://localhost:8080"):
        self.otp_base_url = otp_base_url
        self.plan_url = f"{otp_base_url}/otp/routers/default/plan"
        self.router_info_url = f"{otp_base_url}/otp/routers/default"
        
    async def check_otp_status(self) -> Dict[str, Any]:
        """Check if OTP server is running and get router info"""
        try:
            response = requests.get(self.router_info_url, timeout=10)
            if response.status_code == 200:
                return {
                    "status": "online",
                    "data": response.json()
                }
            else:
                return {
                    "status": "error",
                    "message": f"OTP server returned status {response.status_code}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "offline",
                "message": f"Cannot connect to OTP server: {str(e)}"
            }
    
    async def plan_trip(self, 
                       from_lat: float, 
                       from_lon: float, 
                       to_lat: float, 
                       to_lon: float,
                       mode: str = "TRANSIT",
                       depart_time: Optional[str] = None) -> Dict[str, Any]:
        """Plan a trip using OTP"""
        
        # Check OTP status first
        status = await self.check_otp_status()
        if status["status"] != "online":
            return {
                "success": False,
                "error": f"OTP server is {status['status']}: {status['message']}"
            }
        
        # Prepare request parameters
        params = {
            "fromPlace": f"{from_lat},{from_lon}",
            "toPlace": f"{to_lat},{to_lon}",
            "mode": mode,
            "maxWalkDistance": 1000,  # 1km max walking
            "walkSpeed": 1.4,  # m/s
            "bikeSpeed": 4.0,  # m/s
            "numItineraries": 3,  # Get 3 route options
            "arriveBy": "false",
            "wheelchair": "false"
        }
        
        if depart_time:
            params["date"] = depart_time.split("T")[0] if "T" in depart_time else "2024-01-01"
            params["time"] = depart_time.split("T")[1] if "T" in depart_time else "12:00"
        
        try:
            response = requests.get(self.plan_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_otp_response(data)
            else:
                return {
                    "success": False,
                    "error": f"OTP planning failed with status {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def _parse_otp_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OTP response and extract route information"""
        try:
            if "error" in data:
                return {
                    "success": False,
                    "error": data["error"].get("message", "Unknown OTP error")
                }
            
            itineraries = data.get("plan", {}).get("itineraries", [])
            if not itineraries:
                return {
                    "success": False,
                    "error": "No routes found for the given locations"
                }
            
            routes = []
            for i, itinerary in enumerate(itineraries):
                route = self._parse_itinerary(itinerary, i + 1)
                routes.append(route)
            
            return {
                "success": True,
                "routes": routes,
                "request_time": data.get("plan", {}).get("date", ""),
                "from_place": data.get("plan", {}).get("from", {}),
                "to_place": data.get("plan", {}).get("to", {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse OTP response: {str(e)}"
            }
    
    def _parse_itinerary(self, itinerary: Dict[str, Any], route_num: int) -> Dict[str, Any]:
        """Parse individual itinerary from OTP response"""
        legs = itinerary.get("legs", [])
        total_duration = itinerary.get("duration", 0) / 60  # Convert to minutes
        total_walking_time = sum(leg.get("walkingTime", 0) for leg in legs) / 60
        transfers = sum(1 for leg in legs if leg.get("mode") == "TRANSIT") - 1
        
        # Parse legs for detailed instructions
        leg_details = []
        for leg in legs:
            leg_info = {
                "mode": leg.get("mode", "WALK"),
                "duration": leg.get("duration", 0) / 60,
                "distance": leg.get("distance", 0),
                "from": leg.get("from", {}).get("name", "Unknown"),
                "to": leg.get("to", {}).get("name", "Unknown"),
                "route": leg.get("route", ""),
                "headsign": leg.get("headsign", ""),
                "departure_time": leg.get("startTime", ""),
                "arrival_time": leg.get("endTime", "")
            }
            leg_details.append(leg_info)
        
        return {
            "route_number": route_num,
            "total_duration": round(total_duration, 1),
            "total_walking_time": round(total_walking_time, 1),
            "transfers": max(0, transfers),
            "legs": leg_details,
            "summary": self._generate_route_summary(leg_details)
        }
    
    def _generate_route_summary(self, legs: List[Dict[str, Any]]) -> str:
        """Generate a human-readable summary of the route"""
        summary_parts = []
        
        for leg in legs:
            mode = leg["mode"]
            if mode == "WALK":
                duration = leg["duration"]
                summary_parts.append(f"Walk {duration:.1f} minutes")
            elif mode == "TRANSIT":
                route = leg["route"]
                headsign = leg["headsign"]
                from_place = leg["from"]
                to_place = leg["to"]
                summary_parts.append(f"Take {route} to {headsign} from {from_place} to {to_place}")
            elif mode == "BUS":
                route = leg["route"]
                headsign = leg["headsign"]
                summary_parts.append(f"Take Bus {route} to {headsign}")
        
        return " → ".join(summary_parts)

# Global OTP server instance
otp_server = OTPServer()

async def plan_transit_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float, 
                           mode: str = "TRANSIT", depart_time: Optional[str] = None) -> Dict[str, Any]:
    """Main function to plan transit routes"""
    return await otp_server.plan_trip(from_lat, from_lon, to_lat, to_lon, mode, depart_time)

async def check_otp_connection() -> Dict[str, Any]:
    """Check OTP server connection"""
    return await otp_server.check_otp_status()
