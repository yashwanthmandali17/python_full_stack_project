from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from src
from src.db import Database
from src.logic import BookingLogic, SlotManagement

app = FastAPI(title="EV Charging Slot Booking API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class SlotCreate(BaseModel):
    location: str
    slot_number: int

class BookingCreate(BaseModel):
    slot_id: str
    vehicle_number: str
    vehicle_type: Optional[str] = None

class BookingUpdate(BaseModel):
    booking_status: str

# Initialize services
db = Database()
booking_logic = BookingLogic()
slot_management = SlotManagement()

# Authentication endpoints
@app.post("/register")
async def register(user: UserCreate):
    """Register a new user"""
    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = db.create_user(user.username, user.password, user.role)
    if new_user:
        return {"message": "User registered successfully", "user_id": new_user["id"]}
    else:
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/login")
async def login(credentials: UserLogin):
    """User login"""
    user = db.get_user_by_username(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Account is inactive")
    
    return {
        "message": "Login successful",
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"]
    }

# Slot endpoints
@app.get("/slots")
async def get_slots(available_only: bool = False):
    """Get all slots or available slots only"""
    if available_only:
        slots = booking_logic.get_available_slots()
    else:
        slots = db.get_all_slots()
    return {"slots": slots}

@app.post("/slots")
async def create_slot(slot: SlotCreate, user_id: str):
    """Create a new slot (admin only)"""
    user = db.get_user_by_id(user_id)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = slot_management.create_slot(slot.location, slot.slot_number)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.delete("/slots/{slot_id}")
async def delete_slot(slot_id: str, user_id: str):
    """Delete a slot (admin only)"""
    user = db.get_user_by_id(user_id)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = slot_management.delete_slot(slot_id)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

# Booking endpoints
@app.get("/bookings")
async def get_bookings(user_id: str, admin_view: bool = False):
    """Get bookings - user's own or all (admin)"""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if admin_view and user.get("role") == "admin":
        bookings = db.get_all_bookings()
    else:
        bookings = db.get_user_bookings(user_id)
    
    return {"bookings": bookings}

@app.post("/bookings")
async def create_booking(booking: BookingCreate, user_id: str = None):
    """Create a new booking"""
    # Check if user_id was provided as query parameter
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    result = booking_logic.create_booking(user_id, booking.slot_id, booking.vehicle_number, booking.vehicle_type)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

@app.put("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, user_id: str):
    """Cancel a booking"""
    result = booking_logic.cancel_booking(booking_id, user_id)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["message"])

# Dashboard endpoints
@app.get("/dashboard/user/{user_id}")
async def get_user_dashboard(user_id: str):
    """Get user dashboard data"""
    dashboard_data = booking_logic.get_user_dashboard(user_id)
    return dashboard_data

@app.get("/dashboard/admin")
async def get_admin_dashboard(user_id: str):
    """Get admin dashboard data"""
    user = db.get_user_by_id(user_id)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_data = booking_logic.get_admin_dashboard()
    return dashboard_data

@app.get("/")
async def root():
    return {"message": "EV Charging Slot Booking API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)