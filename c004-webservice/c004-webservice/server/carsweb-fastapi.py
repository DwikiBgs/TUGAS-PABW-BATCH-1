# server/carsweb-fastapi.py

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from peewee import *
from typing import Optional, List
import uvicorn
import os

# ============ DATABASE CONFIGURATION ============
# Path ke database (berada di folder yang sama)
db_path = os.path.join(os.path.dirname(__file__), 'carsweb.db')
db = SqliteDatabase(db_path)

class BaseModelDB(Model):
    class Meta:
        database = db

class TBCarsWeb(BaseModelDB):
    carname = TextField()
    carbrand = TextField()
    carmodel = TextField()
    carprice = TextField()

# ============ PYDANTIC SCHEMA ============
class CarCreate(BaseModel):
    carname: str
    carbrand: str
    carmodel: str
    carprice: str

class CarUpdate(BaseModel):
    carname: Optional[str] = None
    carbrand: Optional[str] = None
    carmodel: Optional[str] = None
    carprice: Optional[str] = None

class CarResponse(BaseModel):
    id: int
    carname: str
    carbrand: str
    carmodel: str
    carprice: str

# ============ FASTAPI APP ============
app = FastAPI(
    title="Car Data Web Service",
    description="CRUDS API for Car Data using FastAPI and SQLite",
    version="1.0.0"
)

# ============ ROOT ENDPOINT ============
@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Car Data Web Service is running!",
        "endpoints": {
            "GET /cars": "Read all cars",
            "GET /cars/?search=keyword": "Search cars",
            "GET /cars/{id}": "Get car by ID",
            "POST /cars": "Create new car",
            "PUT /cars/{id}": "Update car by ID",
            "DELETE /cars/{id}": "Delete car by ID"
        },
        "documentation": "/docs",
        "alternative_documentation": "/redoc"
    }

# ============ CREATE (POST) ============
@app.post("/cars/", response_model=CarResponse, status_code=201)
def create_car(car: CarCreate):
    """Create a new car data"""
    try:
        new_car = TBCarsWeb.create(
            carname=car.carname,
            carbrand=car.carbrand,
            carmodel=car.carmodel,
            carprice=car.carprice
        )
        return CarResponse(
            id=new_car.id,
            carname=new_car.carname,
            carbrand=new_car.carbrand,
            carmodel=new_car.carmodel,
            carprice=new_car.carprice
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating car: {str(e)}")

# ============ READ + SEARCH (GET) ============
@app.get("/cars/", response_model=List[CarResponse])
def read_cars(search: Optional[str] = Query(None, description="Search keyword")):
    """Read all cars or search by keyword"""
    try:
        if search:
            # SEARCH: Filter data berdasarkan keyword
            rows = TBCarsWeb.select().where(
                (TBCarsWeb.carname.contains(search)) |
                (TBCarsWeb.carbrand.contains(search)) |
                (TBCarsWeb.carmodel.contains(search))
            )
        else:
            # READ: Ambil semua data
            rows = TBCarsWeb.select()
        
        cars = []
        for row in rows:
            cars.append(CarResponse(
                id=row.id,
                carname=row.carname,
                carbrand=row.carbrand,
                carmodel=row.carmodel,
                carprice=row.carprice
            ))
        
        return cars
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cars: {str(e)}")

# ============ READ BY ID (GET) ============
@app.get("/cars/{car_id}", response_model=CarResponse)
def read_car_by_id(car_id: int):
    """Get car data by ID"""
    try:
        car = TBCarsWeb.get_by_id(car_id)
        return CarResponse(
            id=car.id,
            carname=car.carname,
            carbrand=car.carbrand,
            carmodel=car.carmodel,
            carprice=car.carprice
        )
    except TBCarsWeb.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Car with ID {car_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ============ UPDATE (PUT) ============
@app.put("/cars/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car: CarUpdate):
    """Update car data by ID"""
    try:
        car_data = TBCarsWeb.get_by_id(car_id)
        
        if car.carname is not None:
            car_data.carname = car.carname
        if car.carbrand is not None:
            car_data.carbrand = car.carbrand
        if car.carmodel is not None:
            car_data.carmodel = car.carmodel
        if car.carprice is not None:
            car_data.carprice = car.carprice
        
        car_data.save()
        
        return CarResponse(
            id=car_data.id,
            carname=car_data.carname,
            carbrand=car_data.carbrand,
            carmodel=car_data.carmodel,
            carprice=car_data.carprice
        )
    except TBCarsWeb.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Car with ID {car_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating car: {str(e)}")

# ============ DELETE (DELETE) ============
@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    """Delete car data by ID"""
    try:
        car_data = TBCarsWeb.get_by_id(car_id)
        car_data.delete_instance()
        
        return {
            "status": "success",
            "message": f"Car with ID {car_id} deleted successfully"
        }
    except TBCarsWeb.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Car with ID {car_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting car: {str(e)}")

# ============ RUN SERVER ============
if __name__ == "__main__":
    uvicorn.run(
        "carsweb-fastapi:app",
        host="0.0.0.0",
        port=5012,
        reload=True
    )