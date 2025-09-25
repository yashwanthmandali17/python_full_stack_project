## EV charging slot booking
A web or desktop application that allows users to book time slots for a single electric vehicle (EV) charging point. Users can check available slots, make bookings, and cancel if needed. Admin manages availability.
## Features
## User Features
- **Check availability** → Calendar or list view of open slots.
- **Book a slot** → Select date and time, confirm booking.
- **Cancel/Reschedule booking** → Change slot if needed.
## Admin Features
- **Manage slots** → Add, edit, or remove available time slots.
- **Monitor bookings** → View all upcoming bookings and user info.
- **Mark unavailable slots** → Temporarily block slots (e.g., maintenance).

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

### Prequisites

-Python 3.8 or higher
-A supabase account
-Git(Push,cloning)

### 1.Clone or download the project

**Option 1:clone with Git**
git clone https://github.com/yashwanthmandali17/python_full_stack_project.git
cd python_full_stack_project

**Option 2:Download and extract the ZIP file**
Go to Github repository,click code-Download ZIP,then extrat it.

### 2.Set Up a Python Virtual Environment
python -m venv venv       # Create virtual environment
Activate the environment:
venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Configure Environment Variables
1.Create a `.env` file in the project root
2.Add your supabase credentials to `.env`:
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key" 

## 5.Run the Application
## Streamlit Frontend
streamlit run frontend/app.py

The app will open in the browser at `http://localhost:8080`

## FastAPI Backend
cd api
python main.py

The api will be available at `http://localhost:8085`

## How to use


## Technical Details

## Technologies Used

- **Frontend**:Streamlit (Python web framework)
- **Backend**:FastAPI (Python Rest API framework)
- **Database**:Supabase (PostgreSQL-based backend-as-a-server)
- **Languages**:Python 3.8+

### Key Components
1. **`src/db.py`**:Database operations
-Handles all CRUD operations with Supabase

2. **`src/logic.py`**:Business logic
-Task validation and processing

### Troubleshooting

1. **Database Issues (src/db.py)**  
   - **Connection Error**: Ensure Supabase URL and API keys are correctly set in environment variables.  
   - **CRUD Failures**: Check table names and schema in Supabase; mismatched column names can cause errors.  
   - **Timeouts**: Verify network connectivity and Supabase service availability.  

2. **Logic Errors (src/logic.py)**  
   - **Validation Fails**: Make sure input data follows expected schema (e.g., required fields, data types).  
   - **Processing Stops**: Check logs for exceptions; wrap critical sections in `try/except` to capture errors.  
   - **Unexpected Behavior**: Add unit tests to confirm business rules are correctly implemented. 

## Common Issues

### Future Enhancements
- **Notifications** – Email or SMS reminders for upcoming bookings.
- **Booking History** – Users can see past and future bookings.
- **Admin Dashboard** – Manage slots and monitor all bookings.
- **Responsive UI** – Mobile-friendly interface with calendar or slot list.
- **Generate reports** - Total bookings per day/week, popular hours.

## Support
if you encounter any issues or have questions:
Mail:yashwanthmandali17@gmail.com
