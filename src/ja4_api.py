from flask import Flask, request, jsonify
from ja4h import to_ja4h
from ja4 import to_ja4
import traceback  # Add this import

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

def handle_tls(data):
    def to_int_list_safe(values):
        """Convert list elements to int, supporting '0x' and str inputs."""
        result = []
        for v in values:
            try:
                if isinstance(v, int):
                    result.append(v)
                elif isinstance(v, str):
                    if v.startswith('0x') or v.startswith('0X'):
                        result.append(int(v, 16))
                    else:
                        result.append(int(v))
            except ValueError:
                continue  # Skip invalid entries
        return result

    def normalize_version(v):
        if isinstance(v, list):
            return v[0]
        return v

    x = {
        'stream': data.get('stream', -1),
        'hl': 'http' if data.get('http_version') == 'HTTP/1.1' else 'http2',
        'quic': data.get('quic', False),
        'version': normalize_version(data.get('version', '0x0304')),
        '_ja3_hashes': {},
        'supported_versions': data.get('supported_versions', []),
        'alpn_list': data.get('alpn_list', []),
        'domain': data.get('domain', '')
    }

    # Normalize inputs to integers
    x['ciphers'] = to_int_list_safe(data.get('ciphers', []))
    x['extensions'] = to_int_list_safe(data.get('extensions', []))

    # Optional: only if extensions contain 0x000d (13 in decimal)
    if 13 in x['extensions'] or '0x000d' in data.get('extensions', []):
        x['signature_algorithms'] = to_int_list_safe(data.get('signature_algorithms', []))

    to_ja4(x, debug_stream=-1)

    return {
        'ja4': x.get('JA4.1', ''),
        'ja4_raw': x.get('JA4_r.1', ''),
        'ja4_original': x.get('JA4_o.1', '')
    }


@app.route('/ja4h', methods=['POST'])
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
        # tls_response = handle_tls(data)

        return jsonify({
            'http': http_response,
            # 'tls': tls_response,
        })

    except Exception as e:
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")  # Detailed logging
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)