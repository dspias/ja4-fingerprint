from flask import Flask, request, jsonify
from ja4h import to_ja4h
from ja4 import to_ja4
import traceback  # Add this import
import subprocess
import json
import os
import time
import signal

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

    return result.get('JA4H', '')

def capture_traffic():
    interface = 'any'
    pcap_file = f"captures/capture_{int(time.time())}.pcap"

    try:
        process = subprocess.Popen(
            ["tshark", "-i", interface, "-f", "tcp port 443", "-w", pcap_file],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )

        return jsonify({"status": "success", "pcap_file": pcap_file, "pid": process.pid})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_tls(data):
    cmd = ["python3", "ja4.py", data['pcap_file'], "-J"]

    try:
        pid = data['pid']
        os.killpg(pid, signal.SIGTERM)

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
        
        # Validate required fields
        # required_fields = ['method', 'http_version', 'headers', 'pcap_file', 'pid']
        required_fields = ['method', 'http_version', 'headers']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        http_response = handle_http(data)
        # tls_response = handle_tls(data)

        return jsonify({
            'ja4h_hash': http_response,
            # 'tls': tls_response,
            'ja4t_hash': None,
        })

    except Exception as e:
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")  # Detailed logging
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route('/tls-probe', methods=['GET'])
def tls_probe():
    response = capture_traffic()

    return response