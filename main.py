import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_live_ip_data(ip_address):
    url = f"http://ip-api.com/json/{ip_address}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# Tumhara Custom API Endpoint Route: /api/rackipapi
@app.route('/api/rackipapi', methods=['GET'])
def rack_ip_api():
    # User se 'ip' parameter lena (e.g., /api/rackipapi?ip=8.8.8.8)
    ip_target = request.args.get('ip')
    
    if not ip_target:
        return jsonify({
            "status": "error", 
            "message": "Kripya IP address 'ip' parameter mein dein. Example: ?ip=8.8.8.8"
        }), 400
        
    data = get_live_ip_data(ip_target)
    
    if data and data.get("status") == "success":
        # Ekdum professional JSON response format
        return jsonify({
            "status": "success",
            "ip": data.get("query"),
            "country": data.get("country"),
            "region": data.get("regionName"),
            "city": data.get("city"),
            "zip": data.get("zip"),
            "isp": data.get("isp"),
            "coordinates": f"{data.get('lat')}, {data.get('lon')}",
            "api_name": "rackipapi"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": "Invalid IP address ya data nahi mila."
        }), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
