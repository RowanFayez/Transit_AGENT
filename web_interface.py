"""
Web interface for Alexandria Transit AI Agent
Simple Flask-based web UI
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import threading
from transit_agent_final import transit_agent

app = Flask(__name__)

# Global event loop for async operations
loop = None

def get_event_loop():
    """Get or create event loop for async operations"""
    global loop
    if loop is None:
        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, daemon=True).start()
    return loop

def run_async(coro):
    """Run async function in the event loop"""
    future = asyncio.run_coroutine_threadsafe(coro, get_event_loop())
    return future.result()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process user query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Process query asynchronously
        response = run_async(transit_agent.process_query(query))
        
        return jsonify({
            'success': True,
            'response': response,
            'query': query
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def system_status():
    """Get system status"""
    try:
        # Check OTP status
        otp_status = run_async(transit_agent.check_otp_status())
        
        # Get geocoder info
        geocoder_stops = len(transit_agent.geocoder.get_all_stops())
        
        return jsonify({
            'otp_status': otp_status,
            'otp_url': transit_agent.otp_url,
            'geocoder_stops': geocoder_stops,
            'status': 'running'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent')
def recent_locations():
    """Get recent locations"""
    try:
        # Get some example locations from geocoder
        all_stops = transit_agent.geocoder.get_all_stops()
        recent = [stop.stop_name for stop in all_stops[:10]]  # First 10 stops as examples
        return jsonify({'recent': recent})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory and HTML file
    import os
    os.makedirs('templates', exist_ok=True)
    
    # Create simple HTML template
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alexandria Transit AI Agent</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .response {
            margin-top: 20px;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 5px;
            white-space: pre-wrap;
            min-height: 100px;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            background-color: #d5dbdb;
            border-radius: 5px;
            font-size: 14px;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
        }
        .examples {
            margin-top: 20px;
            padding: 15px;
            background-color: #e8f4f8;
            border-radius: 5px;
        }
        .examples h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .example {
            margin: 5px 0;
            padding: 5px;
            background-color: white;
            border-radius: 3px;
            cursor: pointer;
        }
        .example:hover {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚌 Alexandria Transit AI Agent</h1>
        
        <div class="input-group">
            <input type="text" id="queryInput" placeholder="Ask about transit routes in Arabic or English..." />
        </div>
        
        <div>
            <button onclick="processQuery()">Get Route</button>
            <button onclick="checkStatus()">Check Status</button>
            <button onclick="getRecent()">Recent Locations</button>
        </div>
        
        <div id="response" class="response" style="display: none;"></div>
        <div id="status" class="status" style="display: none;"></div>
        
        <div class="examples">
            <h3>Example Queries:</h3>
            <div class="example" onclick="setQuery('أريد الذهاب من المنتزه إلى فيكتوريا')">
                أريد الذهاب من المنتزه إلى فيكتوريا
            </div>
            <div class="example" onclick="setQuery('عايز أروح من المنتزه لفيكتوريا')">
                عايز أروح من المنتزه لفيكتوريا
            </div>
            <div class="example" onclick="setQuery('عايزة أروح من سيدي جابر للرمل')">
                عايزة أروح من سيدي جابر للرمل
            </div>
            <div class="example" onclick="setQuery('إزاي أروح من فيكتوريا لسيدي بشر؟')">
                إزاي أروح من فيكتوريا لسيدي بشر؟
            </div>
            <div class="example" onclick="setQuery('How do I go from Montazah to Sidi Gaber?')">
                How do I go from Montazah to Sidi Gaber?
            </div>
            <div class="example" onclick="setQuery('من سيدي جابر إلى الرمل')">
                من سيدي جابر إلى الرمل
            </div>
            <div class="example" onclick="setQuery('Route from Victoria to Raml Station')">
                Route from Victoria to Raml Station
            </div>
        </div>
    </div>

    <script>
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        function processQuery() {
            const query = document.getElementById('queryInput').value.trim();
            if (!query) return;
            
            const responseDiv = document.getElementById('response');
            const statusDiv = document.getElementById('status');
            
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = '<div class="loading">🤔 Processing your request...</div>';
            statusDiv.style.display = 'none';
            
            fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    responseDiv.innerHTML = data.response;
                } else {
                    responseDiv.innerHTML = '❌ Error: ' + data.error;
                }
            })
            .catch(error => {
                responseDiv.innerHTML = '❌ Error: ' + error.message;
            });
        }
        
        function checkStatus() {
            const statusDiv = document.getElementById('status');
            statusDiv.style.display = 'block';
            statusDiv.innerHTML = '<div class="loading">Checking system status...</div>';
            
            fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                statusDiv.innerHTML = `
                    <strong>System Status:</strong><br>
                    OTP Server: ${data.otp_status ? '✅ Running' : '❌ Not Running'}<br>
                    OTP URL: ${data.otp_url}<br>
                    Available Stops: ${data.geocoder_stops}<br>
                    System: ${data.status}
                `;
            })
            .catch(error => {
                statusDiv.innerHTML = '❌ Error checking status: ' + error.message;
            });
        }
        
        function getRecent() {
            const responseDiv = document.getElementById('response');
            responseDiv.style.display = 'block';
            responseDiv.innerHTML = '<div class="loading">Getting recent locations...</div>';
            
            fetch('/api/recent')
            .then(response => response.json())
            .then(data => {
                if (data.recent) {
                    responseDiv.innerHTML = data.recent;
                } else {
                    responseDiv.innerHTML = '❌ Error: ' + data.error;
                }
            })
            .catch(error => {
                responseDiv.innerHTML = '❌ Error: ' + error.message;
            });
        }
        
        // Allow Enter key to submit
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQuery();
            }
        });
    </script>
</body>
</html>
    '''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("🌐 Starting web interface...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
