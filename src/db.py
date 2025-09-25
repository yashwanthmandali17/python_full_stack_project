# db.py
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


# ---------------- USERS TABLE OPERATIONS ---------------- #

# Create a new user
def create_user(name, email, password, vehicle_number, contact_number=None):
    return supabase.table("users").insert({
        "name": name,
        "email": email,
        "password": password,  # hashed password recommended
        "vehicle_number": vehicle_number,
        "contact_number": contact_number
    }).execute()


# Get all users
def get_all_users():
    return supabase.table("users").select("*").order("created_at", desc=True).execute()


# Get user by email (for login/authentication)
def get_user_by_email(email):
    return supabase.table("users").select("*").eq("email", email).execute()


# Update user details
def update_user(user_id, new_data: dict):
    return supabase.table("users").update(new_data).eq("user_id", user_id).execute()


# Delete a user
def delete_user(user_id):
    return supabase.table("users").delete().eq("user_id", user_id).execute()



# ---------------- SLOTS TABLE OPERATIONS ---------------- #

# Create a new slot
def create_slot(date, start_time, end_time, is_available=True):
    return supabase.table("slots").insert({
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "is_available": is_available
    }).execute()


# Get all available slots for a specific date
def get_available_slots(date):
    return supabase.table("slots").select("*") \
        .eq("date", date) \
        .eq("is_available", True) \
        .order("start_time") \
        .execute()


# Mark a slot as unavailable (once booked)
def update_slot_availability(slot_id, is_available):
    return supabase.table("slots").update({"is_available": is_available}).eq("slot_id", slot_id).execute()


# Get all slots
def get_all_slots():
    return supabase.table("slots").select("*").order("date", desc=True).execute()



# ---------------- BOOKINGS TABLE OPERATIONS ---------------- #

# Create a booking
def create_booking(user_id, slot_id, date, start_time, end_time, status="confirmed"):
    return supabase.table("bookings").insert({
        "user_id": user_id,
        "slot_id": slot_id,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "status": status
    }).execute()


# Get all bookings of a user
def get_bookings_by_user(user_id):
    return supabase.table("bookings").select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()


# Get booking by ID
def get_booking_by_id(booking_id):
    return supabase.table("bookings").select("*").eq("booking_id", booking_id).execute()


# Update booking status (confirmed/cancelled/completed)
def update_booking_status(booking_id, status):
    return supabase.table("bookings").update({"status": status}).eq("booking_id", booking_id).execute()


# Delete a booking
def delete_booking(booking_id):
    return supabase.table("bookings").delete().eq("booking_id", booking_id).execute()


# ---------------- REPORTS & LEADERBOARD STYLE QUERIES ---------------- #

# Get upcoming bookings (for dashboard)
def get_upcoming_bookings():
    return supabase.table("bookings").select("*") \
        .order("date", desc=False) \
        .limit(20) \
        .execute()


# Get daily bookings summary (count per date)
def get_daily_booking_summary():
    return supabase.table("bookings").select("date, count:booking_id") \
        .group("date") \
        .order("date", desc=True) \
        .execute()