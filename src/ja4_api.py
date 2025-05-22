from flask import Flask, request, jsonify
from ja4h import to_ja4h
from ja4 import to_ja4
import traceback  # Add this import
import subprocess
import shlex
import json

app = Flask(__name__)

def handle_http(data):
    x = {
        'method': data['method'],
        'hl': 'http' if data['http_version'] == 'HTTP/1.1' else 'h2',
        'headers': data['headers'],
        'cookies': data.get('cookies', []),
        'lang': data.get('lang', ''),
        'stream': -1  # Add this dummy stream value
    }

    result = to_ja4h(x)
    return {
        'ja4h': result.get('JA4H', ''),
        'ja4h_r': result.get('JA4H_r', ''),
        'ja4h_ro': result.get('JA4H_ro', '')
    }

def capture_traffic():
    interface = 'eth0'
    output_file = 'captures/live.pcap'
    duration = 10  # capture 5 seconds of traffic

    try:
        subprocess.run([
            "tshark", "-i", interface,
            "-a", f"duration:{duration}",
            "-w", output_file
        ], check=True)

        return jsonify({
            "status": "success",
            "message": f"Captured traffic to {output_file}"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def handle_tls():
    cmd = ["python3", "ja4.py", "captures/live.pcap", "-J"]

    try:
        capture_traffic()

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        raw_output = result.stdout.strip()

        parsed_data = []
        decoder = json.JSONDecoder()
        idx = 0
        
        # Skip leading whitespace
        while idx < len(raw_output) and raw_output[idx].isspace():
            idx += 1

        # Parse concatenated JSON objects
        while idx < len(raw_output):
            try:
                obj, idx = decoder.raw_decode(raw_output, idx)
                parsed_data.append(obj)
                
                # Skip whitespace between objects
                while idx < len(raw_output) and raw_output[idx].isspace():
                    idx += 1
                    
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"JSON parsing failed at position {idx}: {str(e)}",
                    "partial_data": parsed_data,
                    "raw_output": raw_output
                }

        return {
            "success": True,
            "count": len(parsed_data),
            "data": parsed_data,
            "raw_output": raw_output,
            "code": result.returncode
        }

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": "Command execution failed",
            "stderr": e.stderr,
            "returncode": e.returncode
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "raw_output": raw_output if 'raw_output' in locals() else None
        }


@app.route('/ja4-network-hash', methods=['POST'])
def http():
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")  # Add logging
        
        # Validate required fields
        required_fields = ['method', 'http_version', 'headers']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        http_response = handle_http(data)
        tls_response = handle_tls()

        return jsonify({
            'http': http_response,
            'tls': tls_response,
        })

    except Exception as e:
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")  # Detailed logging
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500