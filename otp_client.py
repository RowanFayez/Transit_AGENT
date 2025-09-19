"""
Async OpenTripPlanner (OTP) client using aiohttp.
Provides: status checks and trip planning with multiple itineraries.
Parses legs and durations correctly (OTP durations are in seconds).
"""

from __future__ import annotations

import aiohttp
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time


@dataclass
class OTPLeg:
    mode: str
    from_name: str
    to_name: str
    duration_min: int
    distance_km: float
    route: Optional[str] = None
    route_short_name: Optional[str] = None
    route_long_name: Optional[str] = None
    headsign: Optional[str] = None
    agency_name: Optional[str] = None
    route_type: Optional[int] = None


@dataclass
class OTPItinerary:
    total_duration_min: int
    total_distance_km: float
    total_walking_time_min: int
    transfers: int
    legs: List[OTPLeg]


class AsyncOTPClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")

    async def check_status(self, session: Optional[aiohttp.ClientSession] = None, timeout: int = 5) -> bool:
        url = f"{self.base_url}/otp/routers/default"
        close_after = False
        sess = session
        if sess is None:
            sess = aiohttp.ClientSession()
            close_after = True
        try:
            async with sess.get(url, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False
        finally:
            if close_after:
                await sess.close()

    async def plan_trip(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float,
        *,
        num_itineraries: int = 3,
        mode: str = "TRANSIT,WALK",
        max_walk_distance: int = 2000,
        arrive_by: bool = False,
        date: Optional[str] = None,
        time_str: Optional[str] = None,
        wheelchair: bool = False,
        timeout: int = 20,
    ) -> Dict[str, Any]:
        """Request trip planning from OTP and return parsed itineraries.

        Returns a dict: { success: bool, error?: str, itineraries?: List[OTPItinerary], raw?: Any }
        """
        params = {
            "fromPlace": f"{from_lat},{from_lon}",
            "toPlace": f"{to_lat},{to_lon}",
            "mode": mode,
            "maxWalkDistance": max_walk_distance,
            "arriveBy": str(arrive_by).lower(),
            "numItineraries": num_itineraries,
            "wheelchair": str(wheelchair).lower(),
        }

        # If date/time not provided, let OTP use server 'now'. Some deployments need explicit values; we try to be resilient.
        if date:
            params["date"] = date
        if time_str:
            params["time"] = time_str

        url = f"{self.base_url}/otp/routers/default/plan"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, timeout=timeout) as resp:
                    status = resp.status
                    data = await resp.json(content_type=None)

                    if status != 200:
                        return {"success": False, "error": f"OTP HTTP {status}", "raw": data}

                    if "error" in data:
                        msg = data.get("error", {}).get("message") or str(data.get("error"))
                        return {"success": False, "error": msg or "OTP returned error", "raw": data}

                    plan = data.get("plan")
                    if not plan:
                        # Common cause: router not ready or no transit found given constraints
                        return {"success": False, "error": "No plan in response (no itineraries)", "raw": data}

                    itineraries = plan.get("itineraries", []) or []
                    if not itineraries:
                        return {"success": False, "error": "No itineraries found", "raw": data}

                    parsed = [self._parse_itinerary(itin) for itin in itineraries]
                    return {"success": True, "itineraries": parsed, "raw": data}
            except aiohttp.ClientError as e:
                return {"success": False, "error": f"Network error: {e}"}
            except Exception as e:
                return {"success": False, "error": f"Unexpected error: {e}"}

    def _parse_itinerary(self, itinerary: Dict[str, Any]) -> OTPItinerary:
        legs = itinerary.get("legs", [])

        # OTP durations are in seconds
        total_duration_min = int(round((itinerary.get("duration", 0) or 0) / 60))
        total_distance_km = sum((leg.get("distance") or 0) for leg in legs) / 1000.0

        # Prefer itinerary.walkTime if present (seconds), else compute from legs where mode == WALK
        walk_time_sec = itinerary.get("walkTime")
        if walk_time_sec is None:
            walk_time_sec = sum((leg.get("duration", 0) or 0) for leg in legs if (leg.get("mode") == "WALK"))
        total_walking_time_min = int(round(walk_time_sec / 60))

        transit_legs = [leg for leg in legs if (leg.get("transitLeg") or leg.get("mode") in {"BUS", "TRAM", "RAIL", "SUBWAY", "FERRY"})]
        transfers = max(0, len(transit_legs) - 1)

        parsed_legs: List[OTPLeg] = []
        for leg in legs:
            duration_min = int(round((leg.get("duration", 0) or 0) / 60))
            distance_km = (leg.get("distance", 0) or 0) / 1000.0
            parsed_legs.append(
                OTPLeg(
                    mode=leg.get("mode", "WALK"),
                    from_name=leg.get("from", {}).get("name", "Unknown"),
                    to_name=leg.get("to", {}).get("name", "Unknown"),
                    duration_min=duration_min,
                    distance_km=distance_km,
                    route=leg.get("route") or leg.get("routeShortName") or leg.get("routeLongName"),
                    route_short_name=leg.get("routeShortName"),
                    route_long_name=leg.get("routeLongName"),
                    headsign=leg.get("headsign"),
                    agency_name=leg.get("agencyName"),
                    route_type=leg.get("routeType"),
                )
            )

        return OTPItinerary(
            total_duration_min=total_duration_min,
            total_distance_km=round(total_distance_km, 2),
            total_walking_time_min=total_walking_time_min,
            transfers=transfers,
            legs=parsed_legs,
        )
