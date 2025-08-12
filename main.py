from sqlite3 import IntegrityError
from sqlalchemy import true
import uvicorn
from logger import logger
from settings import EnvSettings, AppSettings
from services import GeolocationService
from fastapi import Depends, FastAPI, HTTPException
from models import AddressBook, Person, PersonCreate, PersonOutput, PersonUpdate, get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Initialize FastAPI app
app = FastAPI(openapi_tags=AppSettings.APP_METADATA)
app.title = AppSettings.APP_TIITLE
app.description = AppSettings.APP_DESCRIPTION
app.version = AppSettings.APP_VERSION

#Welcome route
@app.get("/",tags=["index"])
async def index() -> dict:
    logger.info("Accessed the welcome route")
    return {"message": "Welcome to the EastVantage API assessment!"}


@app.get("/all_address", response_model=list[PersonOutput],tags=["all_address"])
async def all_address(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[PersonOutput]:
    #fetches all address books with pagination support.
    logger.info(f"Fetching all address books with skip={skip} and limit={limit}")
    try:
        address_books = db.query(Person).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Error fetching address books: {e}")
        raise HTTPException(status_code=500, detail={
            "message":"Internal Server Error",
            "error": str(e)
            })
    
    logger.info("Fetched all address books:", address_books)

    return address_books

# Get address by person ID
@app.get("/get_address/{person_id}", response_model=PersonOutput, tags=["get_address_by_id"])
async def get_address_by_id(person_id: int, db: Session = Depends(get_db)) -> PersonOutput:
   
    logger.info(f"Fetching address for person_id: {person_id}")
    try:
        address_book = db.query(Person).filter(Person.id == person_id).with_for_update().first()
        logger.info(f"Fetched address book: {type(address_book.address.latitude)} {type(address_book.address.longitude)}")
    except Exception as e:
        logger.error(f"Error fetching address for person_id {person_id}: {e}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e),
            "request_id": person_id
            })
    
    logger.info(f"Fetched address book for person_id {person_id}: {address_book}")

    if not address_book:
        logger.error(f"Address not found for person_id: {person_id}")
        raise HTTPException(status_code=404, detail={ 
            "message":"Address not found",
            "person_id": person_id
            })
        
    return address_book

@app.get("/nearby", response_model=list[PersonOutput], tags=["nearby"])
def get_nearby_addresses(latitude: float, longitude: float, distance: float, db: Session = Depends(get_db)) -> list[PersonOutput]:
    #Get addresses within a certain distance from a given latitude and longitude.

    logger.info(f"Fetching addresses within {distance} km of ({latitude}, {longitude})")
    
    try:
        # Fetch addresses within the distance threshold using haversine formula 
        nearby_addresses = db.query(Person).join(AddressBook).where(
            GeolocationService.haversine(
                AddressBook.latitude, AddressBook.longitude,
                latitude, longitude) <= distance).all()
    except Exception as e:
        logger.error(f"{type(latitude)}, {type(longitude)}, {type(distance)}")
        logger.error(f"Error fetching nearby addresses: {e}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e),
            "request_id": f"lat:{latitude}, lon:{longitude}, dist:{distance}"
            })
    
    logger.info(f"Found {len(nearby_addresses)} nearby addresses")

    return nearby_addresses

# Create a new address with personal details
@app.post("/create_address", response_model=PersonCreate, tags=["create_address"])
async def create_address(person: PersonCreate, db:Session=Depends(get_db)) -> PersonCreate:

    # Validate required fields using loops and lists down fields that are empty
    required_fields = [["name", "email", "phone", "address"], ["street", "city", "country"]]
    required_objects = [person, person.address]
    for i in range(len(required_objects)):
        empty_fields = []

        for field in required_fields[i]:
            value = getattr(required_objects[i], field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                empty_fields.append(field)

        if empty_fields:
            raise HTTPException(status_code=400, detail={
                "message": f"Please provide valid value(s) for: {', '.join(empty_fields)}"
            })
            
    # Generate latitude and longitude for the address using geocoding service  
    logger.info(f"Geocoding address for person: {person} address: {person.address}")
    try:
        address = f"{person.address.street}, {person.address.city}, {person.address.postal}, {person.address.country}"
        latitude, longitude = GeolocationService.geocode_address(address)
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "message":"Internal server error",
            "error": str(e)
        })
    
    logger.info(f"Geocoded address to latitude: {latitude}, longitude: {longitude}")


    # Attempt to add the new person and address to the database. This block is designed to avoid race conditions and duplicate entries that can occur
    try:
        new_address = AddressBook(
            person_id=0,
            city=person.address.city,
            country=person.address.country,
            street=person.address.street,
            postal=person.address.postal,
            latitude=latitude,
            longitude=longitude
        )

        new_person = Person(
            name=person.name,
            email=person.email,
            phone=person.phone,
            address=new_address
        )

        new_address.person_id = new_person.id
        db.add(new_person)
        db.add(new_address)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Person already exist {e}")
        
        raise HTTPException(status_code=400, detail={
            "message": "Integrity error",
            "error": "Integrity error (possibly duplicate email) ",
            "request_id": person.email
        })
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating address: {e}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e),
            "request_id": person.email
        })

    return new_person   

# Update an existing address
@app.put("/update_address/{person_id}", response_model=PersonUpdate, tags=["update_address"])
async def update_address(person_id: int, person: PersonUpdate, db: Session = Depends(get_db)) -> PersonUpdate:
    
    try:
        # Use row-level locking to prevent concurrent updates
        existing_person = db.query(Person).filter(Person.id == person_id).with_for_update().first()
    except Exception as e:
        logger.error(f"Error fetching person with ID {person_id}: {e}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e),
            "request_id": person_id
        })

    if not existing_person:
        raise HTTPException(status_code=404, detail={
            "person_id": person_id,
            "message": "Person not found"
        })

    logger.info(f"Updating address for person_id: {person_id} with data: {person}")

    # Validate and update fields
    if person.name:
        existing_person.name = person.name
    if person.email:
        existing_person.email = person.email
    if person.phone:
        existing_person.phone = person.phone
    if person.address:
        address = existing_person.address
        if person.address.city:
            address.city = person.address.city
        if person.address.country:
            address.country = person.address.country
        if person.address.street:
            address.street = person.address.street
        if person.address.postal:
            address.postal = person.address.postal

    try:
        if person.address:
            # Generate latitude and longitude for the address using geocoding service for updated address
            new_street = person.address.street or existing_person.address.street
            new_city = person.address.city or existing_person.address.city
            new_postal = person.address.postal or existing_person.address.postal
            new_country = person.address.country or existing_person.address.country
            print("asdsad")
            latitude, longitude = GeolocationService.geocode_address(f"{new_street}, {new_city}, {new_postal}, {new_country}")

            address.latitude = latitude
            address.longitude = longitude

        db.commit()
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating person: {e}")
        raise HTTPException(status_code=400, detail={
            "message": "Integrity error (possibly duplicate email)",
            "error": str(e),
            "person_id": person_id
        })
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating address: {e}")
        raise HTTPException(status_code=500, detail={
            "message": "Internal Server Error",
            "error": str(e),
            "person_id": person_id
        })

    return existing_person

#Delete an address by person ID 
@app.delete("/delete_address/{person_id}", tags=["delete_address"])
async def delete_address(person_id: int, db: Session = Depends(get_db)) -> dict:

    # Fetches and locks the person row to safely handle concurrent deletes and avoid race conditions.
    try:
        existing_person = db.query(Person).filter(Person.id == person_id).with_for_update().first()
    except Exception as e:
        logger.error(f"Error fetching person with ID {person_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    if not existing_person:
        raise HTTPException(status_code=404, detail={
            "message": "Person not found",
            "person_id": person_id
            })
    
    logger.info(f"Deleting address for person_id: {person_id}")
    db.delete(existing_person)
    db.commit()
    return {"message": "Address deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=EnvSettings.HOST, port=int(EnvSettings.PORT), reload=AppSettings.APP_RELOAD, timeout_keep_alive=AppSettings.APP_TIMEOUT)