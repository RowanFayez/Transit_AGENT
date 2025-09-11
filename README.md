# 🚌 Alexandria Transit AI Agent

A smart AI-powered transit assistant for Alexandria, Egypt that helps users find public transportation routes using natural language queries in Arabic, Egyptian Arabic, and English.

## 🌟 Features

- **Trilingual Support**: Arabic, Egyptian Arabic, and English
- **Real-time Route Planning**: Integration with OpenTripPlanner (OTP)
- **Comprehensive GTFS Data**: 400+ transit stops across Alexandria
- **Smart Location Recognition**: Fuzzy matching and geocoding
- **Web Interface**: User-friendly Flask-based web application
- **Memory System**: Remembers user preferences and recent locations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Java 8 or higher (for OpenTripPlanner)
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RowanFayez/Transit_AGENT.git
   cd Transit_AGENT
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
    Copy the example env file, then edit `.env` to add your keys:
   
    - Windows (PowerShell):
       ```powershell
       Copy-Item env_example.txt .env
       ```
    - macOS/Linux:
       ```bash
       cp env_example.txt .env
       ```
   
    Required variables in `.env`:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    OTP_BASE_URL=http://localhost:8080
    MEMORY_FILE=user_memory.json
    ```

### Running the Application

#### Option 1: Web Interface (Recommended)

1. **Start the web application:**
   ```bash
   python web_interface.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

#### Option 2: Command Line Interface

1. **Run the agent directly:**
   ```bash
   python agent.py
   ```

2. **Or test the final version:**
   ```bash
   python test_final.py
   ```

## 🗺️ OpenTripPlanner Setup (Optional)

For detailed route planning with real transit data:

1. **Download OTP:**
   - Download OTP JAR file from [OpenTripPlanner](https://github.com/opentripplanner/OpenTripPlanner)
   - Place it in your project directory

2. **Prepare GTFS data:**
   - Download Alexandria GTFS data
   - Place it in the `otp_data` directory

3. **Start OTP server:**
   ```bash
   java -Xmx4G -jar otp-2.2.0-shaded.jar --build "otp_data" --serve
   ```

4. **Verify OTP is running:**
   - Open http://localhost:8080 in your browser
   - You should see the OTP interface

