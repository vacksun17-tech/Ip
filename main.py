import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# State name se Vehicle RTO Code map karne ki dictionary
VEHICLE_MAP = {
    "maharashtra": "MH", "delhi": "DL", "uttar pradesh": "UP", "bihar": "BR", 
    "madhya pradesh": "MP", "rajasthan": "RJ", "punjab": "PB", "haryana": "HR",
    "gujarat": "GJ", "karnataka": "KA", "tamil nadu": "TN", "west bengal": "WB",
    "telangana": "TS", "andhra pradesh": "AP", "kerala": "KL", "odisha": "OD",
    "california": "CA (USA)", "texas": "TX (USA)", "new york": "NY (USA)"
}

def fetch_source(url, parser_func):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            return parser_func(res.json())
    except Exception:
        pass
    return "Source Offline/Rate Limited"

@app.route('/api/rackipapi', methods=['GET'])
def rack_ip_api():
    ip = request.args.get('ip')
    if not ip:
        return jsonify({"status": "error", "message": "Kripya ?ip=8.8.8.8 dalein."}), 400

    # 1. IP-API.com
    s1 = fetch_source(f"http://ip-api.com/json/{ip}", lambda d: {
        "country": d.get("country"), "region": d.get("regionName"), "city": d.get("city"), "isp": d.get("isp"), "zip": d.get("zip")
    } if d.get("status") == "success" else None)

    # 2. IPAPI.co
    s2 = fetch_source(f"https://ipapi.co/{ip}/json/", lambda d: {
        "country": d.get("country_name"), "region": d.get("region"), "city": d.get("city"), "isp": d.get("org"), "asn": d.get("asn")
    } if not d.get("error") else None)

    # 3. IP.Guide
    s3 = fetch_source(f"https://ip.guide/{ip}", lambda d: {
        "country": d.get("location", {}).get("country"), "city": d.get("location", {}).get("city"), "isp": d.get("network", {}).get("name"), "asn": d.get("network", {}).get("asn")
    })

    # 4. IPWHOIS.io
    s4 = fetch_source(f"https://ipwhois.app/json/{ip}", lambda d: {
        "country": d.get("country"), "region": d.get("region"), "city": d.get("city"), "isp": d.get("isp"), "type": d.get("type")
    } if d.get("success") else None)

    # 5. IPinfo.io
    s5 = fetch_source(f"https://ipinfo.io/{ip}/json", lambda d: {
        "city": d.get("city"), "region": d.get("region"), "country": d.get("country"), "isp": d.get("org"), "loc": d.get("loc")
    })

    # 6. SeeIP.org
    s6 = fetch_source(f"https://api.seeip.org/geoip/{ip}", lambda d: {
        "country": d.get("country"), "region": d.get("region"), "city": d.get("city"), "isp": d.get("organization"), "postal": d.get("postal_code")
    })

    # 7. IP-API.com Advanced Intel
    s7 = fetch_source(f"http://ip-api.com/json/{ip}?fields=status,continent,countryCode,currency,callingCode,asname", lambda d: {
        "continent": d.get("continent"), "country_short": d.get("countryCode"), "currency_code": d.get("currency"), "phone_code": f"+{d.get('callingCode')}" if d.get('callingCode') else None, "as_name": d.get("asname")
    } if d.get("status") == "success" else None)

    # 8. MEGA SOURCE: ENTERPRISE CYBER INTEL
    s8 = fetch_source(f"http://ip-api.com/json/{ip}?fields=status,timezone,offset,currency,proxy,hosting,mobile", lambda d: {
        "timezone_name": d.get("timezone"), "timezone_offset_seconds": d.get("offset"), "currency_name": d.get("currency"), "is_vpn_or_proxy": "Yes" if d.get("proxy") else "No", "is_hosting_server": "Yes" if d.get("hosting") else "No", "is_mobile_data": "Yes" if d.get("mobile") else "No"
    } if d.get("status") == "success" else None)

    # 9. FRAUD RISK ANALYSIS
    s9 = fetch_source(f"https://ipwhois.app/json/{ip}", lambda d: {
        "fraud_risk_score": "High Risk" if d.get("security", {}).get("anonymous", False) or d.get("proxy") else "Low Risk / Clean IP",
        "connection_type": d.get("type", "Broadband/Cellular"),
        "is_tor_network": "Yes" if d.get("security", {}).get("tor", False) else "No"
    } if d.get("success") else {"fraud_risk_score": "Low Risk / Clean IP"})

    # 10. CUSTOM VEHICLE RTO & ISO REGION AGGREGATOR
    region_name = ""
    if isinstance(s1, dict) and s1.get("region"):
        region_name = s1.get("region").lower()
    elif isinstance(s4, dict) and s4.get("region"):
        region_name = s4.get("region").lower()
        
    v_code = VEHICLE_MAP.get(region_name, "Unknown / Outside Major Database")
    
    s10 = {
        "detected_region_state": region_name.title() if region_name else "Unknown",
        "expected_vehicle_plate_prefix": v_code,
        "is_indian_rto_applicable": "Yes" if v_code in VEHICLE_MAP.values() and len(v_code)==2 else "No"
    }

    return jsonify({
        "status": "success",
        "ip": ip,
        "api_name": "rackipapi_ultimate_v10",
        "total_sources_integrated": 10,
        "results": {
            "source_1_ipapi_com": s1,
            "source_2_ipapi_co": s2,
            "source_3_ip_guide": s3,
            "source_4_ipwhois": s4,
            "source_5_ipinfo_io": s5,
            "source_6_seeip": s6,
            "source_7_deep_intel_mix": s7,
            "source_8_mega_enterprise_intel": s8,
            "source_9_fraud_risk_score": s9,
            "source_10_vehicle_rto_intel": s10
        },
        # 🔥 TUMHARI OWNERSHIP CREDIT FIELD 🔥
        "credits": {
            "owner": "@kihoerack",
            "admin": "@YeuIin"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
