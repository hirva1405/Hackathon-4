from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="Traveloop Complete API")

# Allow React to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, change to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── PYDANTIC SCHEMAS ──────────────────────────────────────────────

class User(BaseModel):
    name: str
    email: str
    photo: Optional[str] = None
    language: str

class City(BaseModel):
    id: int
    name: str
    country: str
    region: str
    costIndex: str
    popularity: int
    emoji: str
    desc: str

class Activity(BaseModel):
    id: int
    name: str
    type: str
    cost: int
    duration: str
    city: str
    desc: str

class Stop(BaseModel):
    id: int
    city: str
    country: str
    days: int
    emoji: str
    activities: List[str] = []
    budget: int = 0

class Budget(BaseModel):
    transport: int = 0
    stay: int = 0
    activities: int = 0
    meals: int = 0
    total: int = 0

class ChecklistItem(BaseModel):
    id: int
    item: str
    category: str
    packed: bool = False

class Note(BaseModel):
    id: int
    title: str
    body: str
    date: str

class Trip(BaseModel):
    id: int
    name: str
    description: str
    cover: str = "🌍"
    startDate: str
    endDate: str
    status: str = "planning"
    shared: bool = False
    stops: List[Stop] = []
    budget: Budget = Budget()
    checklist: List[ChecklistItem] = []
    notes: List[Note] = []

# ─── IN-MEMORY DATABASES (Mocking a real DB) ───────────────────────

db_user = User(name="Arjun Mehta", email="arjun@traveloop.io", language="English")

db_cities = [
    {"id": 1, "name": "Tokyo", "country": "Japan", "region": "Asia", "costIndex": "High", "popularity": 98, "emoji": "🗾", "desc": "Ultra-modern city blending tradition and technology."},
    {"id": 2, "name": "Paris", "country": "France", "region": "Europe", "costIndex": "High", "popularity": 97, "emoji": "🗼", "desc": "The city of lights, art, and haute cuisine."},
    {"id": 3, "name": "Bali", "country": "Indonesia", "region": "Asia", "costIndex": "Low", "popularity": 92, "emoji": "🌴", "desc": "Tropical paradise with temples and surf."},
    {"id": 4, "name": "New York", "country": "USA", "region": "Americas", "costIndex": "High", "popularity": 96, "emoji": "🗽", "desc": "The city that never sleeps."},
    {"id": 5, "name": "Barcelona", "country": "Spain", "region": "Europe", "costIndex": "Medium", "popularity": 91, "emoji": "🌊", "desc": "Gaudi's masterpieces and Mediterranean beaches."},
]

db_activities = [
    {"id": 1, "name": "City Walking Tour", "type": "Sightseeing", "cost": 25, "duration": "3h", "city": "Any", "desc": "Explore hidden gems with a local guide."},
    {"id": 2, "name": "Food & Street Market Tour", "type": "Food", "cost": 45, "duration": "4h", "city": "Any", "desc": "Taste authentic local flavors and street eats."},
    {"id": 3, "name": "Scuba Diving Introduction", "type": "Adventure", "cost": 95, "duration": "4h", "city": "Coastal", "desc": "First dive experience in crystal-clear waters."},
]

db_admin_stats = {
    "totalUsers": 12480, "totalTrips": 34210, "citiesVisited": 187, "avgBudget": 2840,
    "topCities": [
        {"city": "Tokyo", "trips": 4210}, {"city": "Paris", "trips": 3980}, {"city": "Bali", "trips": 3540},
    ],
    "monthly": [
        {"month": "Jan", "trips": 2100}, {"month": "Feb", "trips": 2400}, {"month": "Mar", "trips": 3800},
        {"month": "Apr", "trips": 3200}, {"month": "May", "trips": 2900}, {"month": "Jun", "trips": 3600},
    ],
}

db_trips: List[Trip] = [
    Trip(
        id=1, name="Japan Sakura Chase", description="Follow the cherry blossoms from Tokyo to Kyoto.", cover="🌸",
        startDate="2025-03-20", endDate="2025-04-02", status="completed", shared=True,
        stops=[ Stop(id=1, city="Tokyo", country="Japan", days=5, emoji="🗾", activities=["Shibuya Crossing"], budget=1200) ],
        budget=Budget(transport=1800, stay=1600, activities=520, meals=480, total=4400),
        checklist=[], notes=[]
    )
]

# ─── API ROUTES ────────────────────────────────────────────────────

@app.get("/")
def read_root():
    """This fixes the 'Not Found' error when visiting localhost:8000/"""
    return {
        "status": "online",
        "message": "Traveloop API is running! Visit http://localhost:8000/docs to see all endpoints."
    }

# --- User Routes ---
@app.get("/api/user", response_model=User)
def get_user():
    return db_user

@app.put("/api/user", response_model=User)
def update_user(updated_user: User):
    global db_user
    db_user = updated_user
    return db_user

# --- Explore Routes ---
@app.get("/api/cities", response_model=List[City])
def get_cities():
    return db_cities

@app.get("/api/activities", response_model=List[Activity])
def get_activities():
    return db_activities

# --- Admin Routes ---
@app.get("/api/admin/stats")
def get_admin_stats():
    return db_admin_stats

# --- Trip Routes ---
@app.get("/api/trips", response_model=List[Trip])
def get_trips():
    return db_trips

@app.get("/api/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: int):
    for trip in db_trips:
        if trip.id == trip_id:
            return trip
    raise HTTPException(status_code=404, detail="Trip not found")

@app.post("/api/trips", response_model=Trip)
def create_trip(trip_in: Trip):
    new_id = max([t.id for t in db_trips], default=0) + 1
    trip_in.id = new_id
    db_trips.insert(0, trip_in)
    return trip_in

@app.put("/api/trips/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, updated_trip: Trip):
    for index, trip in enumerate(db_trips):
        if trip.id == trip_id:
            db_trips[index] = updated_trip
            return updated_trip
    raise HTTPException(status_code=404, detail="Trip not found")

@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: int):
    for index, trip in enumerate(db_trips):
        if trip.id == trip_id:
            del db_trips[index]
            return {"message": "Trip deleted successfully"}
    raise HTTPException(status_code=404, detail="Trip not found")