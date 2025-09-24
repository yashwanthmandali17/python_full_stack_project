<!-- # EV charging slot booking -->
A web or desktop application that allows users to book time slots for a single electric vehicle (EV) charging point. Users can check available slots, make bookings, and cancel if needed. Admin manages availability.
## Features
-User Features
-Check availability → Calendar or list view of open slots.
-Book a slot → Select date and time, confirm booking.
-Cancel/Reschedule booking → Change slot if needed.
-Booking history → View past and upcoming bookings.
-Admin Features
-Manage slots → Add, edit, or remove available time slots.
-Monitor bookings → View all upcoming bookings and user info.
-Mark unavailable slots → Temporarily block slots (e.g., maintenance).
-Generate reports → Total bookings per day/week, popular hours.

## Project Structure
```
EV charging slot booking/
|
|----src/           # core application logic
|   |----logic.py   # business logic and task operations
|   |----db.py      # database operations
|
|----api/           # Backend API
|   |----main.py    # FastAPI endpoints
|
|----frontend/      # Frontend application
|   |----app.py     # Streamlit web interface
|
|---requirements.txt # Python Dependencies
|
|----README.md     # Project documentation
|
|----.env          # Python Variables
```
## Quick Start

## Prequisites

-Python 3.8 or higher
-A supabase account
-Git(Push,cloning)

## 1.Clone or download the project

# Option 1:clone with Git
git clone https://github.com/yashwanthmandali17/python_full_stack_project.git
# Option 2:Download and extract the ZIP file

## 2.Install Dependencies
# Install all required python packages
pip install -r requirements.txt

## 3.Setup supabase database

1.Create supabase project

2.create tasks table:
-Go to the SQL Editor
-Run the SQL command:
sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    vehicle_number VARCHAR(20) NOT NULL,
    contact_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

## 4.Configure Environment variables
1.Create a `.env` file in the project root
2.Add your supabase credentials to `.env`:
SUPABASE_URL=""
SUPABASE_KEY="" 

## 5.Run the Application
## Streamlit Frontend
streamlit run frontend/app.py

The app will open in the browser at ``

## FastAPI Backend
cd api
python main.py

The api will be available at ``

## How to use


## Technical Details

## Technologies Used

- **Frontend**:Streamlit (Python web framework)
- **Backend**:FastAPI (Python Rest API framework)
- **Database**:Supabase (PostgreSQL-based backend-as-a-server)
-**Languages**:Python 3.8+

### Key Components
1. **`src/db.py`**:Database operations
-Handles all CRUD operations with Supabase

2. **`src/logic.py`**:Business logic
-Task validation and processing

## Troubleshooting

## Common Issues

## Future Enhancements
-Notifications – Email or SMS reminders for upcoming bookings.
-Booking History – Users can see past and future bookings.
-Admin Dashboard – Manage slots and monitor all bookings.
-Responsive UI – Mobile-friendly interface with calendar or slot list.

## Support
if you encounter any issues or have questions:
