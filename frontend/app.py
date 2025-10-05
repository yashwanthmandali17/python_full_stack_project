import streamlit as st
import requests
import json
from datetime import datetime
import os

# API configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="EV Charging Slot Booking",
    page_icon="⚡",
    layout="wide"
)

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def check_api_health():
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_api_request(endpoint, method="GET", data=None, params=None):
    """Helper function to make API requests"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        # Debug output
        print(f"Making {method} request to {url}")
        print(f"Params: {params}")
        print(f"Data: {data}")
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            # For POST requests, include params in the URL and data in JSON body
            response = requests.post(url, params=params, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, params=params, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, timeout=10)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                st.error(f"API Error ({response.status_code}): {error_detail}")
            except:
                st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def login(username, password):
    """User login"""
    data = {"username": username, "password": password}
    result = make_api_request("/login", "POST", data)
    
    if result:
        st.session_state.user_id = result.get("user_id")
        st.session_state.username = result.get("username")
        st.session_state.role = result.get("role")
        st.session_state.logged_in = True
        st.success("Login successful!")
        st.rerun()

def logout():
    """User logout"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.logged_in = False
    st.rerun()

def register(username, password, role="user"):
    """User registration"""
    data = {"username": username, "password": password, "role": role}
    result = make_api_request("/register", "POST", data)
    
    if result:
        st.success("Registration successful! Please login.")

def user_dashboard():
    """User dashboard"""
    st.title("⚡ EV Charging Slot Booking")
    st.subheader(f"Welcome, {st.session_state.username}!")
    
    # Debug: Check if user_id is available
    if not st.session_state.user_id:
        st.error("❌ User ID not found in session. Please log in again.")
        if st.button("Logout and Login Again"):
            logout()
        return
    
    # Get dashboard data
    dashboard_data = make_api_request(f"/dashboard/user/{st.session_state.user_id}")
    
    if dashboard_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Bookings", dashboard_data.get("total_bookings", 0))
        with col2:
            st.metric("Upcoming Bookings", len(dashboard_data.get("upcoming_bookings", [])))
        with col3:
            st.metric("Past Bookings", len(dashboard_data.get("past_bookings", [])))
    else:
        st.warning("Could not load dashboard data")
    
    # Tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["Book Slot", "My Bookings", "Available Slots", "Profile"])
    
    with tab1:
        st.header("Book a Charging Slot")
        
        # Debug: Show current user info
        st.sidebar.write("### Current User Info")
        st.sidebar.write(f"User ID: {st.session_state.user_id}")
        st.sidebar.write(f"Username: {st.session_state.username}")
        st.sidebar.write(f"Role: {st.session_state.role}")
        
        # Get available slots
        slots_data = make_api_request("/slots", params={"available_only": True})
        available_slots = slots_data.get("slots", []) if slots_data else []
        
        if available_slots:
            with st.form("booking_form", clear_on_submit=True):
                st.subheader("New Booking")
                
                col1, col2 = st.columns(2)
                with col1:
                    # Create slot options with better formatting
                    slot_options = {}
                    for slot in available_slots:
                        key = f"{slot['location']} - Slot {slot['slot_number']}"
                        slot_options[key] = slot['id']
                    
                    selected_slot_label = st.selectbox("Select Charging Slot", options=list(slot_options.keys()))
                    slot_id = slot_options[selected_slot_label] if selected_slot_label else None
                    
                    vehicle_number = st.text_input("Vehicle Registration Number", 
                                                 placeholder="AP01BB2006",
                                                 max_chars=20)
                    
                with col2:
                    vehicle_type = st.selectbox("Vehicle Type", 
                                              ["Car", "Bike", "Scooter", "Truck", "Other"])
                    
                    booking_notes = st.text_area("Additional Notes", 
                                               placeholder="E.g., Need fast charging support",
                                               height=100)
                
                st.write("---")
                submit_button = st.form_submit_button("📅 Book Slot Now", type="primary")
                
                if submit_button:
                    if not vehicle_number.strip():
                        st.error("❌ Please enter your vehicle registration number")
                    elif not slot_id:
                        st.error("❌ Please select a charging slot")
                    else:
                        # Show loading spinner
                        with st.spinner("Creating your booking..."):
                            # Prepare booking data
                            booking_data = {
                                "slot_id": slot_id,
                                "vehicle_number": vehicle_number.strip(),
                                "vehicle_type": vehicle_type
                            }
                            
                            # DEBUG: Show what's being sent
                            with st.expander("🔧 Debug Information"):
                                st.write("**Request Details:**")
                                st.json({
                                    "endpoint": "/bookings",
                                    "method": "POST",
                                    "params": {"user_id": st.session_state.user_id},
                                    "data": booking_data
                                })
                            
                            # Make the API request with user_id as query parameter
                            result = make_api_request(
                                "/bookings", 
                                method="POST", 
                                data=booking_data, 
                                params={"user_id": st.session_state.user_id}
                            )
                            
                            if result and result.get("success"):
                                st.success("✅ Booking confirmed successfully!")
                                st.balloons()
                                st.info(f"Booking ID: {result.get('booking', {}).get('id', 'N/A')}")
                                # Refresh the page to show updated slots
                                st.rerun()
                            else:
                                error_msg = result.get('message', 'Unknown error') if result else 'No response from server'
                                st.error(f"❌ Failed to create booking: {error_msg}")
        
        else:
            st.info("📭 No available charging slots at the moment.")
            st.write("Please check back later or contact administrator for more slots.")
    
    with tab2:
        st.header("My Bookings")
        
        if dashboard_data:
            upcoming = dashboard_data.get("upcoming_bookings", [])
            past = dashboard_data.get("past_bookings", [])
            
            st.subheader("Upcoming Bookings")
            if upcoming:
                for booking in upcoming:
                    # Handle timestamp formatting safely
                    created_at = booking.get('created_at')
                    if created_at:
                        try:
                            # Remove 'Z' and add timezone offset if needed
                            if 'Z' in created_at:
                                created_at = created_at.replace('Z', '+00:00')
                            formatted_time = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
                        except:
                            formatted_time = "Unknown"
                    else:
                        formatted_time = "Unknown"
                    
                    with st.expander(f"Booking {booking['id'][:8]} - {booking.get('vehicle_number', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Slot:** {booking.get('charging_slots', {}).get('location', 'N/A')} - Slot {booking.get('charging_slots', {}).get('slot_number', 'N/A')}")
                            st.write(f"**Vehicle:** {booking.get('vehicle_number', 'N/A')} ({booking.get('vehicle_type', 'N/A')})")
                        with col2:
                            st.write(f"**Status:** {booking.get('booking_status', 'N/A')}")
                            st.write(f"**Booked on:** {formatted_time}")
                        
                        if booking.get('booking_status') == 'confirmed':
                            if st.button("Cancel Booking", key=f"cancel_{booking['id']}"):
                                result = make_api_request(f"/bookings/{booking['id']}/cancel", "PUT", params={"user_id": st.session_state.user_id})
                                if result:
                                    st.success("Booking cancelled successfully!")
                                    st.rerun()
            else:
                st.info("No upcoming bookings.")
            
            st.subheader("Past Bookings")
            if past:
                for booking in past:
                    # Handle timestamp formatting safely
                    created_at = booking.get('created_at')
                    if created_at:
                        try:
                            if 'Z' in created_at:
                                created_at = created_at.replace('Z', '+00:00')
                            formatted_time = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
                        except:
                            formatted_time = "Unknown"
                    else:
                        formatted_time = "Unknown"
                    
                    with st.expander(f"Booking {booking['id'][:8]} - {booking.get('vehicle_number', 'N/A')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Slot:** {booking.get('charging_slots', {}).get('location', 'N/A')} - Slot {booking.get('charging_slots', {}).get('slot_number', 'N/A')}")
                            st.write(f"**Vehicle:** {booking.get('vehicle_number', 'N/A')} ({booking.get('vehicle_type', 'N/A')})")
                        with col2:
                            st.write(f"**Status:** {booking.get('booking_status', 'N/A')}")
                            st.write(f"**Booked on:** {formatted_time}")
            else:
                st.info("No past bookings.")
        else:
            st.warning("Could not load booking data")
    
    with tab3:
        st.header("Available Slots")
        slots_data = make_api_request("/slots", params={"available_only": True})
        available_slots = slots_data.get("slots", []) if slots_data else []
        
        if available_slots:
            st.subheader(f"Found {len(available_slots)} available slot(s)")
            for slot in available_slots:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**📍 {slot['location']} - Slot {slot['slot_number']}**")
                with col2:
                    st.success("✅ Available")
                st.write("---")
        else:
            st.info("No available slots at the moment.")
    
    with tab4:
        st.header("Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Account Information")
            st.info(f"**Username:** {st.session_state.username}")
            st.info(f"**Role:** {st.session_state.role}")
            st.info(f"**User ID:** {st.session_state.user_id}")
        
        with col2:
            st.subheader("Actions")
            if st.button("🔄 Refresh Data", type="secondary"):
                st.rerun()
            
            if st.button("🚪 Logout", type="primary"):
                logout()

def admin_dashboard():
    """Admin dashboard"""
    st.title("⚡ EV Charging Slot Booking - Admin Panel")
    st.subheader(f"Welcome, Admin {st.session_state.username}!")
    
    # Get admin dashboard data
    dashboard_data = make_api_request("/dashboard/admin", params={"user_id": st.session_state.user_id})
    
    if dashboard_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Slots", dashboard_data.get("total_slots", 0))
        with col2:
            st.metric("Available Slots", dashboard_data.get("available_slots", 0))
        with col3:
            st.metric("Booked Slots", dashboard_data.get("booked_slots", 0))
        with col4:
            st.metric("Today's Bookings", len(dashboard_data.get("today_bookings", [])))
    else:
        st.warning("Could not load admin dashboard data")
    
    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Manage Slots", "View Bookings", "Add New Slot", "Profile"])
    
    with tab1:
        st.header("Manage Charging Slots")
        
        slots_data = make_api_request("/slots")
        slots = slots_data.get("slots", []) if slots_data else []
        
        if slots:
            st.subheader(f"Total Slots: {len(slots)}")
            for slot in slots:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                with col1:
                    st.write(f"**{slot['location']} - Slot {slot['slot_number']}**")
                with col2:
                    status = "Available" if slot['is_available'] else "Booked"
                    color = "🟢" if slot['is_available'] else "🔴"
                    st.write(f"{color} {status}")
                with col3:
                    slot_id_short = slot['id'][:8] + "..."
                    st.write(f"ID: `{slot_id_short}`")
                with col4:
                    if st.button("Delete", key=f"delete_{slot['id']}", type="secondary"):
                        result = make_api_request(f"/slots/{slot['id']}", "DELETE", params={"user_id": st.session_state.user_id})
                        if result:
                            st.success("Slot deleted successfully!")
                            st.rerun()
                st.write("---")
        else:
            st.info("No slots configured. Add your first slot in the 'Add New Slot' tab.")
    
    with tab2:
        st.header("All Bookings")
        
        bookings_data = make_api_request("/bookings", params={"user_id": st.session_state.user_id, "admin_view": True})
        bookings = bookings_data.get("bookings", []) if bookings_data else []
        
        if bookings:
            st.subheader(f"Total Bookings: {len(bookings)}")
            for booking in bookings:
                # Handle timestamp formatting safely
                created_at = booking.get('created_at')
                if created_at:
                    try:
                        if 'Z' in created_at:
                            created_at = created_at.replace('Z', '+00:00')
                        formatted_time = datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_time = "Unknown"
                else:
                    formatted_time = "Unknown"
                
                with st.expander(f"Booking {booking['id'][:8]} - {booking.get('user', {}).get('username', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**User:** {booking.get('user', {}).get('username', 'N/A')}")
                        st.write(f"**Slot:** {booking.get('charging_slots', {}).get('location', 'N/A')} - Slot {booking.get('charging_slots', {}).get('slot_number', 'N/A')}")
                    with col2:
                        st.write(f"**Vehicle:** {booking.get('vehicle_number', 'N/A')}")
                        st.write(f"**Type:** {booking.get('vehicle_type', 'N/A')}")
                    with col3:
                        status = booking.get('booking_status', 'N/A')
                        status_color = "🟢" if status == 'confirmed' else "🟡" if status == 'completed' else "🔴"
                        st.write(f"**Status:** {status_color} {status}")
                        st.write(f"**Booked on:** {formatted_time}")
                    
                    if booking.get('booking_status') == 'confirmed':
                        if st.button("Cancel Booking", key=f"admin_cancel_{booking['id']}"):
                            result = make_api_request(f"/bookings/{booking['id']}/cancel", "PUT", params={"user_id": st.session_state.user_id})
                            if result:
                                st.success("Booking cancelled successfully!")
                                st.rerun()
        else:
            st.info("No bookings found.")
    
    with tab3:
        st.header("Add New Slot")
        
        with st.form("add_slot_form", clear_on_submit=True):
            st.subheader("Create New Charging Slot")
            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("Location", placeholder="e.g., Main Station, Downtown, Mall")
            with col2:
                slot_number = st.number_input("Slot Number", min_value=1, step=1, value=1)
            
            if st.form_submit_button("➕ Add Slot", type="primary"):
                if location.strip() and slot_number > 0:
                    result = make_api_request("/slots", "POST", {
                        "location": location.strip(),
                        "slot_number": int(slot_number)
                    }, params={"user_id": st.session_state.user_id})
                    
                    if result:
                        st.success("Slot added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add slot. Please try again.")
                else:
                    st.error("Please fill all fields correctly")
    
    with tab4:
        st.header("Admin Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Account Information")
            st.success(f"**Username:** {st.session_state.username}")
            st.success(f"**Role:** {st.session_state.role}")
            st.success(f"**User ID:** {st.session_state.user_id}")
        
        with col2:
            st.subheader("Administrative Actions")
            if st.button("🔄 Refresh All Data", type="secondary"):
                st.rerun()
            
            if st.button("📊 System Status", type="secondary"):
                # Quick system status check
                slots_data = make_api_request("/slots")
                bookings_data = make_api_request("/bookings", params={"user_id": st.session_state.user_id, "admin_view": True})
                
                if slots_data and bookings_data:
                    st.info(f"System Status: ✅ Operational")
                    st.info(f"Total Slots: {len(slots_data.get('slots', []))}")
                    st.info(f"Total Bookings: {len(bookings_data.get('bookings', []))}")
            
            if st.button("🚪 Logout", type="primary"):
                logout()

def login_page():
    """Login/Registration page"""
    st.title("⚡ EV Charging Slot Booking System")
    
    # API health check
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
        st.info("**To fix this:**")
        st.write("1. Open a new terminal in VS Code")
        st.write("2. Run: `cd api && python main.py`")
        st.write("3. Wait for 'Uvicorn running on http://0.0.0.0:8000' message")
        st.write("4. Then refresh this page")
        return
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("🔑 Login", type="primary"):
                if username and password:
                    login(username, password)
                else:
                    st.error("Please enter both username and password")
        
        # Demo credentials
        with st.expander("Demo Credentials"):
            st.write("**Admin Account:**")
            st.code("Username: admin\nPassword: admin123")
            st.write("**Or register a new user account**")
    
    with tab2:
        st.header("Register")
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", type="password", placeholder="Choose a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            role = st.selectbox("Account Type", ["user", "admin"])
            
            if st.form_submit_button("📝 Register", type="primary"):
                if username and password:
                    if password == confirm_password:
                        if len(password) >= 4:
                            register(username, password, role)
                        else:
                            st.error("Password must be at least 4 characters long")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill all fields")

def main():
    """Main application logic"""
    
    # Check if backend is running
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the FastAPI server first.")
        st.info("**To fix this:**")
        st.write("1. Open a new terminal in VS Code")
        st.write("2. Run: `cd api && python main.py`")
        st.write("3. Wait for 'Uvicorn running on http://0.0.0.0:8000' message")
        st.write("4. Then refresh this page")
        return
    
    # Show appropriate page based on login status
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()