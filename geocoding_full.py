#!/usr/bin/env python3
"""
Full Geocoding system for Alexandria Transit with all GTFS stops
"""

import csv
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
import re

@dataclass
class TransitStop:
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    aliases: List[str]

class AlexandriaGeocoder:
    """Full geocoder with all Alexandria GTFS stops"""
    
    def __init__(self):
        self.stops = self._load_all_alexandria_stops()
        self.stop_dict = self._create_stop_dictionary()
    
    def _load_all_alexandria_stops(self) -> List[TransitStop]:
        """Load all Alexandria stops from GTFS data"""
        stops_data = [
            (1, "Borg Al-Arab Old Terminal", 30.883987, 29.497864),
            (2, "Baheeg Square", 30.901450, 29.544387),
            (3, "Al-Marwa Mosque", 30.903941, 29.5475212),
            (4, "Baheeg Traffic Department", 30.942326, 29.5933765),
            (5, "King Heights", 30.948885, 29.606113),
            (6, "Om Zeghyo", 31.0713418, 29.7615553),
            (7, "Al-Madfan", 31.0751035, 29.7532603),
            (8, "Al-Masaken", 31.076461, 29.747692),
            (9, "Al-Emam Al-Shafaay Azhari Institute", 31.077242, 29.744465),
            (10, "Awal Al-Tawkeel", 31.073307, 29.759550),
            (11, "Zoro Cafe", 31.077735, 29.740312),
            (12, "Kilo 21", 31.07786, 29.737498),
            (13, "Street 6 Asafra", 31.265459, 30.00321),
            (17, "Asafra Station", 31.269167, 30.00663),
            (21, "Asafra Station", 31.267844, 30.009992),
            (32, "Street 45 - Miami Bridge", 31.267516, 30.000048),
            (48, "Abu Qir Station", 31.320357, 30.062969),
            (50, "Abu Qir Club", 31.318915, 30.062263),
            (52, "Abu Qir Train Station", 31.317801, 30.061648),
            (54, "AAST Intersection", 31.30886, 30.058856),
            (56, "Abu Qir Engineering Company", 31.315975, 30.060867),
            (58, "Administration Station", 31.304387, 30.057650),
            (60, "Street 16 (Montazah)", 31.302066, 30.062691),
            (61, "El Sadat Mosque Abu Qir", 31.300619, 30.056728),
            (63, "Al Souq Entrance Abu Qir", 31.296131, 30.054943),
            (65, "Al Maamoura", 31.291855, 30.052065),
            (67, "Al Islah", 31.284620, 30.039818),
            (69, "Maamoura Children Park", 31.284028, 30.035003),
            (71, "Maamoura Gates", 31.283503, 30.027416),
            (73, "Street 25 Entrance", 31.261930, 30.071091),
            (75, "Al Montazah Train Station", 31.282523, 30.020785),
            (77, "El Mandara Bridge", 31.280395, 30.016220),
            (79, "El Mandara", 31.280875, 30.015126),
            (81, "El Mandara South", 31.276085, 30.017597),
            (83, "School of Islamic Studies", 31.271116, 30.023042),
            (85, "Al Milaha", 31.264476, 30.027827),
            (87, "Al Berolos Canal", 31.273371, 30.058551),
            (88, "Street 45 Asafra", 31.261259, 30.010096),
            (90, "Street 45 Asafra Church", 31.260051, 30.011648),
            (92, "Oqba Ibn Nafea Hospital", 31.261862, 30.009202),
            (94, "Street 18 Asafra", 31.262648, 30.007861),
            (96, "Abu Omar Pastry Asafra", 31.264053, 30.005483),
            (98, "Asafra Station", 31.270327, 30.005421),
            (100, "Asafra Train Station", 31.273157, 30.008148),
            (101, "El Mandara Square", 31.280202, 30.012224),
            (102, "Sheraton Montazah", 31.281670, 30.010697),
            (104, "Water Company El Mandara", 31.279722, 30.009345),
            (106, "Makram Ice Cream El Mandara", 31.277990, 30.007133),
            (108, "El Nasreya El Qadema", 30.998390, 29.787749),
            (110, "El Tayeb El Nasreya", 31.001647, 29.785412),
            (112, "Green Gate El Nasreya", 31.006483, 29.792355),
            (114, "Amreya Hospital", 31.011924, 29.798221),
            (116, "Amreya Station", 31.009607, 29.805425),
            (119, "El Ola Company Amreya", 31.005577, 29.804039),
            (120, "Amreya Bridge", 31.020498, 29.794159),
            (122, "Izbat Hawd 10", 31.243673, 30.048265),
            (123, "Shahd El Maleka", 31.259586, 30.018943),
            (125, "King House Cafe", 31.261659, 30.022582),
            (127, "Awel 45", 31.269795, 30.998139),
            (129, "Azza Asafra", 31.274639, 30.001705),
            (131, "Gad Asafra", 31.271908, 29.999123),
            (133, "Skandar Ibrahim - Courniche", 31.270267, 29.993477),
            (135, "Izbet Hawd 12", 31.259442, 30.054319),
            (136, "Mostafa Kamel - 45 Street", 31.258351, 30.015979),
            (138, "Al Amrawy Mosque", 31.256301, 30.013529),
            (140, "Mostafa Kamel - Al Bahreya St", 31.253418, 30.010225),
            (142, "Misr Gas Station - Mostafa Kamel", 31.248387, 30.003204),
            (144, "Alexandria Agricultural School", 31.250890, 30.007194),
            (146, "Khorshid", 31.198029, 30.036089),
            (148, "Khorshid Central", 31.196838, 30.039171),
            (150, "Asher Men Ramadan St", 31.261717, 29.998549),
            (151, "Faisal Police Station Asafrah", 31.263019, 29.999528),
            (152, "Gehan Square", 31.261919, 29.993007),
            (154, "Awel Gamal Abdelnaser St", 31.269692, 30.001663),
            (155, "Bahary (Ras Al Tin)", 31.202041, 29.876082),
            (157, "Navy Forces - Bahary", 31.203677, 29.874700),
            (158, "Al Sheikh Wafiq - Bahary", 31.204122, 29.875741),
            (160, "Fathallah - Bahary", 31.204925, 29.877454),
            (162, "Alexandria Navy Scouts", 31.206091, 29.878518),
            (164, "Qasr Sakafet El Anfoshy", 31.209847, 29.879240),
            (165, "Anfoushy Police Station", 31.209968, 29.881695),
            (167, "Carrefour - Desert Road", 31.16851, 29.934719),
            (169, "Elite Hospital", 31.172732, 29.943355),
            (171, "El Bambi", 31.175488, 29.948260),
            (173, "IBCA International School", 31.178913, 29.955883),
            (175, "Awayed Post Office", 31.211489, 30.008273),
            (178, "Al Maraghi", 31.208809, 30.020825),
            (180, "Al Rahma St - Khorshid", 31.206258, 30.029978),
            (182, "Farouq Cafe - Courniche", 31.203867, 29.885535),
            (184, "Fish Market - Courniche", 31.202045, 29.887846),
            (186, "Court Complex - Courniche", 31.201110, 29.889844),
            (188, "El Mansheya Station", 31.199740, 29.895185),
            (190, "Raml Station", 31.200331, 29.899098),
            (192, "Raml Station - Courniche", 31.201157, 29.898789),
            (194, "French Consulate", 31.200503, 29.895198),
            (196, "Al Khaledeen - Courniche", 31.203164, 29.902062),
            (198, "Misr Gas Station - Courniche", 31.206635, 29.905654),
            (200, "Dental School", 31.203854, 29.906754),
            (201, "Al Khaledeen", 31.202897, 29.902976),
            (202, "El Mansheya Station", 31.199353, 29.895700),
            (203, "Miami - Courniche", 31.270044, 29.991522),
            (205, "Ber Masoud", 31.269314, 29.987113),
            (207, "Abu Dhabi Bank - Sidi Bishr", 31.265591, 29.987159),
            (209, "Sidi Bishr Beach", 31.262307, 29.984377),
            (211, "Mohamed Naguib Square", 31.259311, 29.980898),
            (214, "Al Rahman Mosque - Courniche", 31.257247, 29.978774),
            (216, "Sidi Bishr Tram Station", 31.252996, 29.976843),
            (218, "Al Mahrousa Tunnel", 31.254816, 29.975639),
            (220, "San Stefano", 31.246068, 29.965570),
            (222, "Luran Station", 31.249398, 29.971624),
            (223, "Quta (Soter)", 31.208106, 29.906747),
            (225, "Alexandria University - Courniche", 31.210804, 29.912727),
            (227, "Shatby Hospital Mosque", 31.208828, 29.912733),
            (229, "Shatby Pedestrian Tunnel", 31.211945, 29.916118),
            (231, "Gleem Pedestrian Tunnel", 31.240982, 29.959533),
            (233, "Mohandeseen Pedestrian Tunnel", 31.239174, 29.954171),
            (235, "Sun Rise Hotel", 31.232975, 29.946202),
            (237, "Stanley Bridge", 31.236206, 29.950122),
            (239, "The Walk - Sidi Gaber", 31.227199, 29.938278),
            (241, "Camp Shezar", 31.215374, 29.921719),
            (243, "Sporting - Courniche", 31.221021, 29.930492),
            (245, "Cleopatra Pedestrian Bridge", 31.224575, 29.935015),
            (247, "Hanuvil Gameaya", 31.111973, 29.758809),
            (248, "Al Gomrok Police Station", 31.198555, 29.882496),
            (249, "Hany Village", 31.031522, 29.785609),
            (251, "Free Zone", 31.036524, 29.782195),
            (253, "Bab Wahed", 31.200951, 29.881302),
            (254, "El Malaha - Asafra", 31.268037, 30.018908),
            (255, "Tamween Montazah", 31.258167, 29.987767),
            (257, "Sidi Bishr Station", 31.256865, 29.991403),
            (261, "Victoria Station", 31.248845, 29.980624),
            (263, "Victoria College", 31.247678, 29.978304),
            (265, "E-Post Victora", 31.251207, 29.984817),
            (267, "Al Seyouf", 31.241168, 29.997369),
            (268, "Abou Kamal - Al Seyouf", 31.240992, 29.998336),
            (270, "Falaki - Al Seyouf", 31.241222, 29.998835),
            (271, "Madares St - Al Seyouf", 31.237967, 29.999014),
            (273, "Al Seyouf Square", 31.24058, 29.992509),
            (274, "El Saah Square", 31.244342, 29.985606),
            (279, "B-Tech Mostafa Kamel", 31.246437, 29.992494),
            (281, "Malak Hefny St", 31.253722, 29.988864),
            (283, "Street 15", 31.251034, 29.991799),
            (284, "Jewelery Museum", 31.239650, 29.964262),
            (286, "Bakus", 31.235818, 29.966513),
            (291, "Al Wezara Tram", 31.231895, 29.956418),
            (293, "Abu Suliman", 31.232121, 29.982893),
            (295, "Health Insurance Al Seyouf", 31.230062, 29.993247),
            (296, "Pedestrian Bridge - Ring Road", 31.213357, 29.993606),
            (298, "Awayed Bridge Start", 31.215669, 29.994044),
            (300, "El Awayed", 31.217499, 29.993861),
            (304, "El Awayed Bridge End", 31.222197, 29.993587),
            (308, "Entry to Abu Suliman", 31.224578, 29.979563),
            (310, "Namos Bridge", 31.223723, 29.975230),
            (313, "Gabriel Station Bazar", 31.238525, 29.976290),
            (314, "Bait Al Gomla Market", 31.238747, 29.979583),
            (315, "Wekala Ishterakeya", 31.238474, 29.982424),
            (317, "Al Hagar Pedestrian Bridge", 31.220301, 29.965052),
            (320, "Victor Emmanuel Square", 31.214177, 29.944853),
            (323, "Sidi Gaber Station", 31.218117, 29.941997),
            (328, "Abis Bridge", 31.203670, 29.993991),
            (330, "Abis Traffic Light", 31.174897, 29.979008),
            (332, "Anany Factory", 31.180540, 29.991436),
            (334, "Ezbet Saad", 31.207976, 29.941022),
            (337, "Admon Fremon St", 31.208387, 29.947496),
            (339, "Gyad Club", 31.213487, 29.949469),
            (341, "Mansour Opel Car Showroom", 31.225213, 29.94755),
            (343, "Green Plaza", 31.209124, 29.962998),
            (345, "Itihad Club", 31.203727, 29.975989),
            (347, "Ali Ibn Taleb Mosque - Smouha", 31.212550, 29.940482),
            (349, "Ibrahimeya Fly-over", 31.208693, 29.934206),
            (351, "Hadra", 31.204794, 29.936128),
            (352, "Antoniadis", 31.203226, 29.94066),
            (355, "El Mansheya", 31.197631, 29.892740),
            (356, "Gamarek Club", 31.193035, 29.885117),
            (357, "Darwish Factory", 31.188877, 29.886331),
            (358, "Train Station (Al Shohadaa)", 31.193563, 29.90258),
            (363, "Kafr Ashry", 31.181795, 29.884821),
            (365, "Al Wardiyan", 31.162603, 29.866732),
            (367, "Al Gamal Mosque", 31.168011, 29.869020),
            (369, "Al Wardiyan Police Station", 31.164115, 29.863724),
            (371, "Dish Horus", 31.167953, 29.872415),
            (373, "Al Qibary Bridge", 31.176825, 29.879121),
            (375, "Fatma Al Zahraa - Marsa Matrouh Rd", 31.108534, 29.785294),
            (377, "Agamy Star", 31.110251, 29.787984),
            (379, "Al Bitash", 31.114477, 29.794305),
            (382, "Shahr Al Asal", 31.133050, 29.783860),
            (383, "Port Gate", 31.122073, 29.805347),
            (385, "Royal Complex Hall", 31.128322, 29.813366),
            (387, "Fahmy Restaurant", 31.133528, 29.819134),
            (388, "Al Mohandes Mall", 31.135012, 29.821644),
            (389, "Mostaamara", 31.065189, 29.816408),
            (391, "Abdel Kader Entrance", 31.078725, 29.842012),
            (393, "Abdel Kader Station", 31.073021, 29.850206),
            (395, "Toshky Entrance", 31.091200, 29.852864),
            (397, "Abis 8", 31.127255, 29.942771),
            (398, "High Speed Rail Station", 31.153356, 29.922601),
            (400, "Karmouz Hospital", 31.187331, 29.894223),
            (402, "Alexandria Stadium", 31.196257, 29.912830),
            (404, "Moharam Bek Bridge", 31.192872, 29.923180),
            (406, "Suez Canal Pedestrian Bridge", 31.195490, 29.920153),
            (409, "Bab Sharq", 31.201252, 29.915987),
            (412, "Rahman Mosque", 31.205654, 29.909955),
            (413, "Misr Gas Station - Ibrahimeya", 31.207772, 29.929426),
            (415, "Sharqi Water Station", 31.200104, 29.919192),
            (416, "Hadra", 31.201377, 29.93336),
            (418, "Kabo", 31.199118, 29.933344),
            (420, "Karmus", 31.179512, 29.901565),
            (423, "Moharam Bek", 31.183812, 29.926513),
            (425, "El Mawqaf El Geded", 31.180134, 29.913627),
            (429, "Nozha Administration", 31.188251, 29.938024),
            (431, "Seka Hadeed Bridge", 31.197434, 29.953859),
            (434, "Navy Police Station", 31.124783, 29.894353),
            (436, "Maks Post Office", 31.151076, 29.841783),
            (438, "Italian Hospital", 31.199889, 29.925672),
            (439, "Mazroa Gold", 31.232776, 29.961750),
            (440, "Victoria Station", 31.249111, 29.980477),
            (441, "Baheeg Square", 30.901623, 29.544311),
            (442, "Al-Milaha", 31.263673, 30.028506),
            (443, "Egyptian Red Crescent - Bakus", 31.230842, 29.972046),
            (444, "El-Rassafa", 31.191188, 29.91891),
            (445, "El Awayed", 31.218703, 29.994491),
            (446, "Al Seyouf", 31.241104, 29.997384),
            (447, "Falaki - Al Seyouf", 31.241375, 29.998826)
        ]
        
        stops = []
        for stop_id, stop_name, lat, lon in stops_data:
            # Generate aliases for each stop
            aliases = self._generate_aliases(stop_name)
            stops.append(TransitStop(str(stop_id), stop_name, lat, lon, aliases))
        
        return stops
    
    def _generate_aliases(self, stop_name: str) -> List[str]:
        """Generate aliases for a stop name"""
        aliases = [stop_name, stop_name.lower()]
        
        # Arabic translations and common variations
        arabic_translations = {
            "Station": ["محطة", "استيشن"],
            "Hospital": ["مستشفى", "هوسبيتال"],
            "School": ["مدرسة", "سكوله"],
            "Club": ["نادي", "كلوب"],
            "Bridge": ["كوبري", "جسر"],
            "Square": ["ميدان", "سكوير"],
            "Mosque": ["مسجد", "جامع"],
            "Police": ["شرطة", "بوليس"],
            "University": ["جامعة", "يونيفرسيتي"],
            "Post Office": ["مكتب بريد", "بوسطة"],
            "Gas Station": ["محطة بنزين", "جازيره"],
            "Tunnel": ["نفق", "تونيل"],
            "Market": ["سوق", "ماركت"],
            "Mall": ["مول", "سنتر"],
            "Factory": ["مصنع", "فابريكا"],
            "Gate": ["بوابة", "جيت"],
            "Cafe": ["كافيه", "قهوة"],
            "Restaurant": ["مطعم", "ريستوران"]
        }
        
        # Location-specific aliases
        location_aliases = {
            "Victoria": ["فيكتوريا", "فيكتوري"],
            "Montazah": ["المنتزه", "منتزه", "منتزة"],
            "Sidi Gaber": ["سيدي جابر", "سيدى جابر"],
            "Raml": ["الرمل", "رمل"],
            "Mansheya": ["المنشية", "منشية"],
            "Sidi Bishr": ["سيدي بشر", "سيدى بشر"],
            "Gleem": ["جليم"],
            "Sporting": ["السبورتنج", "سبورتنج"],
            "Smouha": ["سموحة"],
            "Karmouz": ["كرموز"],
            "Abu Qir": ["أبو قير", "ابو قير"],
            "Agamy": ["العجمي"],
            "Stanley": ["ستانلي"],
            "San Stefano": ["سان ستيفانو"],
            "Miami": ["ميامي"],
            "Bahary": ["البحري"],
            "Asafra": ["العصفرة"],
            "Mandara": ["المندرة"],
            "Amreya": ["العامرية"],
            "Falaki": ["الفلكي", "فلكي"],
            "Seyouf": ["السيوف"],
            "Khorshid": ["خورشيد"]
        }
        
        # Add English variations
        name_parts = stop_name.split()
        for part in name_parts:
            aliases.append(part.lower())
            
            # Add Arabic translations
            for eng, ara_list in arabic_translations.items():
                if eng.lower() in part.lower():
                    aliases.extend(ara_list)
            
            # Add location aliases
            for eng, ara_list in location_aliases.items():
                if eng.lower() in part.lower():
                    aliases.extend(ara_list)
        
        # Remove duplicates and empty strings
        return list(set([alias for alias in aliases if alias]))
    
    def _create_stop_dictionary(self) -> Dict[str, TransitStop]:
        """Create a dictionary for fast lookup"""
        stop_dict = {}
        for stop in self.stops:
            # Add all aliases as keys
            for alias in stop.aliases:
                stop_dict[alias.lower()] = stop
        return stop_dict
    
    def geocode(self, location_name: str) -> Optional[Tuple[float, float, str]]:
        """Geocode a location name to coordinates"""
        location_lower = location_name.lower().strip()
        
        # Direct lookup
        if location_lower in self.stop_dict:
            stop = self.stop_dict[location_lower]
            return stop.stop_lat, stop.stop_lon, stop.stop_name
        
        # Fuzzy matching
        for alias, stop in self.stop_dict.items():
            if alias in location_lower or location_lower in alias:
                return stop.stop_lat, stop.stop_lon, stop.stop_name
        
        # Pattern matching for Arabic names
        arabic_patterns = {
            'الفلكي': 'Falaki',
            'فلكي': 'Falaki',
            'السيوف': 'Seyouf',
            'سيوف': 'Seyouf',
            'سيدي جابر': 'Sidi Gaber',
            'سيدى جابر': 'Sidi Gaber',
            'فيكتوريا': 'Victoria',
            'المنتزه': 'Montazah',
            'منتزه': 'Montazah',
            'الرمل': 'Raml',
            'رمل': 'Raml'
        }
        
        for arabic, english in arabic_patterns.items():
            if arabic in location_lower:
                # Find stop with English name
                for stop in self.stops:
                    if english.lower() in stop.stop_name.lower():
                        return stop.stop_lat, stop.stop_lon, stop.stop_name
        
        return None
    
    def get_all_stops(self) -> List[TransitStop]:
        """Get all stops"""
        return self.stops
    
    def search_stops(self, query: str) -> List[TransitStop]:
        """Search for stops matching a query"""
        query_lower = query.lower()
        matches = []
        
        for stop in self.stops:
            for alias in stop.aliases:
                if query_lower in alias.lower() or alias.lower() in query_lower:
                    if stop not in matches:
                        matches.append(stop)
                    break
        
        return matches
