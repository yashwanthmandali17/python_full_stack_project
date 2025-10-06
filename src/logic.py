from datetime import datetime, timedelta
from .db import Database
from typing import List, Dict, Any, Optional

class BookingLogic:
    def __init__(self):
        self.db = Database()
    
    def validate_booking(self, user_id: str, slot_id: str) -> tuple[bool, str]:
        """Validate if a booking can be made"""
        try:
            # Check if user exists and is active
            user = self.db.get_user_by_id(user_id)
            if not user or not user.get("is_active", True):
                return False, "User not found or inactive"
            
            # Check if slot exists and is available
            slots = self.db.get_all_slots()
            slot = next((s for s in slots if s["id"] == slot_id), None)
            if not slot:
                return False, "Slot not found"
            if not slot.get("is_available", True):
                return False, "Slot is not available"
            
            # Check if user has any active bookings
            user_bookings = self.db.get_user_bookings(user_id)
            active_bookings = [b for b in user_bookings if b.get("booking_status") == "confirmed"]
            if len(active_bookings) >= 3:
                return False, "Maximum 3 active bookings allowed per user"
            
            return True, "Valid"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def create_booking(self, user_id: str, slot_id: str, vehicle_number: str, vehicle_type: str = None) -> Dict[str, Any]:
        """Create a new booking with validation"""
        is_valid, message = self.validate_booking(user_id, slot_id)
        if not is_valid:
            return {"success": False, "message": message}
        
        booking = self.db.create_booking(user_id, slot_id, vehicle_number, vehicle_type)
        if booking:
            return {"success": True, "booking": booking, "message": "Booking created successfully"}
        else:
            return {"success": False, "message": "Failed to create booking"}
    
    def cancel_booking(self, booking_id: str, user_id: str = None) -> Dict[str, Any]:
        """Cancel a booking"""
        try:
            booking = self.db.get_booking_by_id(booking_id)
            if not booking:
                return {"success": False, "message": "Booking not found"}
            
            # Check if user owns the booking (for users) or allow admin to cancel any
            if user_id and booking.get("user_id") != user_id:
                user = self.db.get_user_by_id(user_id)
                if user and user.get("role") != "admin":
                    return {"success": False, "message": "Cannot cancel another user's booking"}
            
            if booking.get("booking_status") != "confirmed":
                return {"success": False, "message": "Only confirmed bookings can be cancelled"}
            
            success = self.db.update_booking_status(booking_id, "cancelled")
            if success:
                return {"success": True, "message": "Booking cancelled successfully"}
            else:
                return {"success": False, "message": "Failed to cancel booking"}
        except Exception as e:
            return {"success": False, "message": f"Error cancelling booking: {str(e)}"}
    
    def get_available_slots(self) -> List[Dict[str, Any]]:
        """Get all available slots"""
        return self.db.get_available_slots()
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard data for user"""
        bookings = self.db.get_user_bookings(user_id)
        upcoming = [b for b in bookings if b.get("booking_status") == "confirmed"]
        past = [b for b in bookings if b.get("booking_status") in ["cancelled", "completed"]]
        
        return {
            "upcoming_bookings": upcoming,
            "past_bookings": past,
            "total_bookings": len(bookings)
        }
    
    def get_admin_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for admin"""
        slots = self.db.get_all_slots()
        bookings = self.db.get_all_bookings()
        
        available_slots = len([s for s in slots if s.get("is_available", True)])
        booked_slots = len([s for s in slots if not s.get("is_available", True)])
        
        today_bookings = [b for b in bookings if 
                         datetime.fromisoformat(b.get("created_at").replace('Z', '+00:00')).date() == datetime.now().date()]
        
        return {
            "total_slots": len(slots),
            "available_slots": available_slots,
            "booked_slots": booked_slots,
            "today_bookings": today_bookings,
            "all_bookings": bookings
        }

class SlotManagement:
    def __init__(self):
        self.db = Database()
    
    def create_slot(self, location: str, slot_number: int) -> Dict[str, Any]:
        """Create a new charging slot"""
        # Check if slot number already exists at location
        slots = self.db.get_all_slots()
        existing_slot = next((s for s in slots if s["location"] == location and s["slot_number"] == slot_number), None)
        if existing_slot:
            return {"success": False, "message": "Slot number already exists at this location"}
        
        slot = self.db.create_charging_slot(location, slot_number)
        if slot:
            return {"success": True, "slot": slot, "message": "Slot created successfully"}
        else:
            return {"success": False, "message": "Failed to create slot"}
    
    def delete_slot(self, slot_id: str) -> Dict[str, Any]:
        """Delete a charging slot"""
        # Check if slot has active bookings
        bookings = self.db.get_all_bookings()
        active_bookings = [b for b in bookings if b.get("slot_id") == slot_id and b.get("booking_status") == "confirmed"]
        
        if active_bookings:
            return {"success": False, "message": "Cannot delete slot with active bookings"}
        
        success = self.db.delete_slot(slot_id)
        if success:
            return {"success": True, "message": "Slot deleted successfully"}
        else:
            return {"success": False, "message": "Failed to delete slot"}