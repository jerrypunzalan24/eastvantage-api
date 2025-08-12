from sqlalchemy import func
import googlemaps
from settings import EnvSettings
from logger import logger

class GeolocationService:
    # Static methods for geolocation and distance calculations
    @staticmethod
    def geocode_address(address: str) -> tuple:
        try:
            gmaps = googlemaps.Client(key=EnvSettings.GOOGLE_MAPS_API_KEY)
            geocode_result = gmaps.geocode(address)
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None
        logger.info(f"Geocoding address: {address}")
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng'] 
            return latitude, longitude
        
        return None
    
    # Static method to calculate distance between two coordinates
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2) -> bool:
        logger.info(f"Calculating distance between ({lat1}, {lon1}) and ({lat2}, {lon2}")
        R = 6371  
        
        return (
        R * func.acos(func.cos(func.radians(lat1)) * func.cos(func.radians(lat2)) *
            func.cos(func.radians(lon2) - func.radians(lon1)) +
            func.sin(func.radians(lat1)) * func.sin(func.radians(lat2))
            )
        )