from dotenv import load_dotenv
import os
load_dotenv()

class EnvSettings:
    HOST: str = os.getenv("HOST")
    PORT: str = os.getenv("PORT")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    TIMEZONE: str = os.getenv("TIMEZONE")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")

class AppSettings:
    APP_TIMEOUT: int = 30
    APP_RELOAD: bool = True
    APP_TIITLE: str = "Address Book API"
    APP_DESCRIPTION: str = "API for managing address book entries"
    APP_VERSION: str = "1.0.0"
    APP_METADATA: list = [
        {
            "name": "all_address",
            "description": "Get all address books with pagination",
        },
        {
            "name": "get_address_by_id",
            "description": "Get address by person ID",
        },
        {
            "name": "nearby",
            "description": "Get nearby addresses based on latitude and longitude and distance",
        },
        {
            "name": "index",
            "description": "Welcome route for the API",
        },
        {
            "name": "create_address",
            "description": "Create a new address with personal details",
        },
        {
            "name": "update_address",
            "description": "Update address by person ID",
        },
        {
            "name": "delete_address",
            "description": "Delete address by person ID",
        }
    ]