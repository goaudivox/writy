import os
import traceback
import jsonschema
import logging
from jsonschema import validate
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
app = Flask(__name__)
from writy import writing_api

def check_syntax(code):
    # Simulate syntax checking, replace with actual logic
    if "syntax_error" in code:
        raise SyntaxError("Detected syntax error")
    
# Initialize Redis
redis = Redis()

# Initialize the limiter with delayed approach and Redis as the storage backend
limiter = Limiter(key_func=get_remote_address, storage_uri='redis://localhost:6379')
limiter.init_app(app)

logging.basicConfig(filename='api.log', level=logging.INFO)

def require_api_key(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = os.getenv('API_KEY')
        if request.headers.get('X-API-KEY') != api_key:
            abort(401)  # Unauthorized access
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flask API!"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        check_syntax(user_message)
        # Simulate successful response
        return jsonify({"response": "Success"})
    except SyntaxError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/execute-code', methods=['POST'])
@require_api_key
def execute_code():
    data = request.get_json()
    code_snippet = data.get("code", "")
    try:
        local_vars = {}
        exec(code_snippet, {"__builtins__": None}, local_vars)
        return jsonify({"result": local_vars.get('result')}), 200
    except SyntaxError as e:
        return jsonify({"error": "Syntax error in the provided code", "details": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error executing code", "details": str(e)}), 500
    
@app.route('/api/data', methods=['POST'])
def data():
    data = request.get_json()
    # Define a JSON Schema for your expected data structure
    schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "number"}
                },
                "required": ["param1"]
            }
        },
        "required": ["command", "parameters"]
    }
    try:
        # Validate incoming JSON data
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        return jsonify({"error": "Invalid data", "message": str(e)}), 400
    return jsonify({"message": "Data received and validated", "yourData": data}), 200

@app.route('/fetch-logs', methods=['GET'])
@require_api_key
def fetch_logs():
    log_file_path = 'application.log'
    try:
        if not os.path.exists(log_file_path):
            open(log_file_path, 'a').close()  # Create the file if it does not exist
        with open(log_file_path, 'r') as file:
            logs = file.read()
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-config', methods=['POST'])
@require_api_key
def update_config():
    data = request.get_json()
    config_key = data.get("key", "")
    config_value = data.get("value", "")
    return jsonify({"message": f"Configuration for {config_key} updated to {config_value}"}), 200

@app.route('/get-config', methods=['GET'])
@require_api_key
def get_config():
    config_key = request.args.get('key')
    config_value = "example_value"  # Placeholder for actual config retrieval
    return jsonify({config_key: config_value}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "up"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    trace = traceback.format_exc()
    return jsonify({"error": str(e), "trace": trace}), 500

@app.route('/modify-code', methods=['POST'])
def modify_code():
    api_key = request.headers.get('X-API-KEY')
    expected_api_key = os.getenv('API_KEY')
    
    if not api_key or api_key != expected_api_key:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_path = data.get("file_path")
    new_code = data.get("new_code")

    if not file_path or not new_code:
        return jsonify({"error": "Missing file path or new code"}), 400

    try:
        with open(file_path, 'w') as file:
            file.write(new_code)
        return jsonify({"message": "File updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/read-file', methods=['POST'])
def read_file():
    api_key = request.headers.get('X-API-KEY')
    expected_api_key = os.getenv('API_KEY')
    
    if not api_key or api_key != expected_api_key:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    file_path = data.get("file_path", "")

    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
     
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    from writing_api import writing_api
app.register_blueprint(writing_api)
