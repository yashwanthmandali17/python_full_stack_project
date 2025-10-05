import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any

load_dotenv()

class Database:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        self.client: Client = create_client(self.url, self.key)
    
    # User operations
    def create_user(self, username: str, password: str, role: str = "user") -> Dict[str, Any]:
        try:
            response = self.client.table("users").insert({
                "username": username,
                "password": password,
                "role": role
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        try:
            response = self.client.table("users").select("*").eq("username", username).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    # Charging slot operations
    def create_charging_slot(self, location: str, slot_number: int) -> Dict[str, Any]:
        try:
            response = self.client.table("charging_slots").insert({
                "location": location,
                "slot_number": slot_number,
                "is_available": True
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating charging slot: {e}")
            return None
    
    def get_all_slots(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("charging_slots").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error getting slots: {e}")
            return []
    
    def get_available_slots(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("charging_slots").select("*").eq("is_available", True).execute()
            return response.data
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def update_slot_availability(self, slot_id: str, is_available: bool) -> bool:
        try:
            response = self.client.table("charging_slots").update({
                "is_available": is_available
            }).eq("id", slot_id).execute()
            return True
        except Exception as e:
            print(f"Error updating slot: {e}")
            return False
    
    def delete_slot(self, slot_id: str) -> bool:
        try:
            response = self.client.table("charging_slots").delete().eq("id", slot_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting slot: {e}")
            return False
    
    # Booking operations
    def create_booking(self, user_id: str, slot_id: str, vehicle_number: str, vehicle_type: str = None) -> Dict[str, Any]:
        try:
            # First, check if slot is available
            slot = self.client.table("charging_slots").select("*").eq("id", slot_id).execute()
            if not slot.data or not slot.data[0]["is_available"]:
                return None
            
            # Create booking
            response = self.client.table("bookings").insert({
                "user_id": user_id,
                "slot_id": slot_id,
                "vehicle_number": vehicle_number,
                "vehicle_type": vehicle_type,
                "booking_status": "confirmed"
            }).execute()
            
            # Mark slot as unavailable
            if response.data:
                self.update_slot_availability(slot_id, False)
            
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating booking: {e}")
            return None
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("bookings").select("*, charging_slots(*)").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting user bookings: {e}")
            return []
    
    def get_all_bookings(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table("bookings").select("*, users(username), charging_slots(*)").execute()
            return response.data
        except Exception as e:
            print(f"Error getting all bookings: {e}")
            return []
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        try:
            update_data = {"booking_status": status}
            if status == "cancelled":
                update_data["cancelled_at"] = "now()"
            
            response = self.client.table("bookings").update(update_data).eq("id", booking_id).execute()
            
            # If cancelled, make slot available again
            if status == "cancelled":
                booking = self.client.table("bookings").select("slot_id").eq("id", booking_id).execute()
                if booking.data:
                    self.update_slot_availability(booking.data[0]["slot_id"], True)
            
            return True
        except Exception as e:
            print(f"Error updating booking: {e}")
            return False
    
    def get_booking_by_id(self, booking_id: str) -> Dict[str, Any]:
        try:
            response = self.client.table("bookings").select("*, users(username), charging_slots(*)").eq("id", booking_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting booking: {e}")
            return None