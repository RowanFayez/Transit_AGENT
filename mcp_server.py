"""
MCP Server for OpenTripPlanner Integration (async)
Uses aiohttp through a shared AsyncOTPClient.
"""

from typing import Dict, Any, Optional
from dataclasses import asdict
import logging

from otp_client import AsyncOTPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OTPServer:
    """Async OTP server wrapper using AsyncOTPClient"""

    def __init__(self, otp_base_url: str = "http://localhost:8080"):
        self.client = AsyncOTPClient(otp_base_url)

    async def check_otp_status(self) -> Dict[str, Any]:
        ok = await self.client.check_status()
        return {"status": "online" if ok else "offline"}

    async def plan_trip(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float,
        mode: str = "TRANSIT,WALK",
        depart_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Split depart_time if provided
        date = time = None
        if depart_time and "T" in depart_time:
            date, time = depart_time.split("T", 1)

        result = await self.client.plan_trip(
            from_lat,
            from_lon,
            to_lat,
            to_lon,
            mode=mode,
            num_itineraries=3,
            max_walk_distance=2000,
            date=date,
            time_str=time,
        )

        if not result.get("success"):
            return {"success": False, "error": result.get("error")}

        # Convert dataclasses to dicts for JSON friendliness
        itineraries = result.get("itineraries", [])
        return {
            "success": True,
            "routes": [
                {
                    "total_duration": it.total_duration_min,
                    "total_distance_km": it.total_distance_km,
                    "total_walking_time": it.total_walking_time_min,
                    "transfers": it.transfers,
                    "legs": [asdict(leg) for leg in it.legs],
                }
                for it in itineraries
            ],
        }


# Global OTP server instance
otp_server = OTPServer()


async def plan_transit_route(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    mode: str = "TRANSIT,WALK",
    depart_time: Optional[str] = None,
) -> Dict[str, Any]:
    """Main function to plan transit routes"""
    return await otp_server.plan_trip(from_lat, from_lon, to_lat, to_lon, mode, depart_time)


async def check_otp_connection() -> Dict[str, Any]:
    """Check OTP server connection"""
    return await otp_server.check_otp_status()
