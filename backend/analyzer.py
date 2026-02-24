from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import time
import psutil

app = Flask(__name__)
CORS(app)


# ======================================================
# PYTHON EXECUTION ENGINE
# ======================================================
def run_python(code, user_input):
    errors = []
    output = ""
    runtime = 0
    memory_used = 0

    # Create temporary Python file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
        temp.write(code.encode())
        filename = temp.name

    start_time = time.time()

    try:
        process = subprocess.Popen(
            ["python", filename],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(
            input=user_input,
            timeout=5
        )

        runtime = round((time.time() - start_time) * 1000, 2)

        # Try to capture memory usage
        try:
            memory_used = psutil.Process(process.pid).memory_info().rss / 1024
        except:
            memory_used = 0

        if stderr:
            errors.append({
                "line": None,
                "type": "RuntimeError",
                "message": stderr.strip()
            })

        output = stdout

    except subprocess.TimeoutExpired:
        process.kill()
        errors.append({
            "line": None,
            "type": "TimeoutError",
            "message": "Execution timed out (5 seconds limit)."
        })

    except Exception as e:
        errors.append({
            "line": None,
            "type": type(e).__name__,
            "message": str(e)
        })

    finally:
        if os.path.exists(filename):
            os.remove(filename)

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "output": output,
        "runtime": runtime,
        "memory": round(memory_used, 2)
    }


# ======================================================
# C EXECUTION ENGINE
# ======================================================
def run_c(code, user_input):
    errors = []
    output = ""
    runtime = 0
    memory_used = 0

    # Create temporary C file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as temp:
        temp.write(code.encode())
        filename = temp.name

    exe_file = filename.replace(".c", "")

    # Compile C code
    compile_process = subprocess.run(
        ["gcc", filename, "-o", exe_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # If compilation error
    if compile_process.stderr:
        errors.append({
            "line": None,
            "type": "CompilationError",
            "message": compile_process.stderr.strip()
        })

        if os.path.exists(filename):
            os.remove(filename)

        return {
            "success": False,
            "errors": errors,
            "output": "",
            "runtime": 0,
            "memory": 0
        }

    # Run executable
    start_time = time.time()

    try:
        process = subprocess.Popen(
            [exe_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(
            input=user_input,
            timeout=5
        )

        runtime = round((time.time() - start_time) * 1000, 2)

        try:
            memory_used = psutil.Process(process.pid).memory_info().rss / 1024
        except:
            memory_used = 0

        if stderr:
            errors.append({
                "line": None,
                "type": "RuntimeError",
                "message": stderr.strip()
            })

        output = stdout

    except subprocess.TimeoutExpired:
        process.kill()
        errors.append({
            "line": None,
            "type": "TimeoutError",
            "message": "Execution timed out (5 seconds limit)."
        })

    except Exception as e:
        errors.append({
            "line": None,
            "type": type(e).__name__,
            "message": str(e)
        })

    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)

        if os.path.exists(exe_file):
            os.remove(exe_file)

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "output": output,
        "runtime": runtime,
        "memory": round(memory_used, 2)
    }


# ======================================================
# MAIN ROUTE
# ======================================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    code = data.get("code", "")
    language = data.get("language", "")
    user_input = data.get("input", "")

    if language == "python":
        result_data = run_python(code, user_input)

    elif language == "c":
        result_data = run_c(code, user_input)

    else:
        result_data = {
            "success": False,
            "errors": [{
                "line": None,
                "type": "UnsupportedLanguage",
                "message": "Language not supported"
            }],
            "output": "",
            "runtime": 0,
            "memory": 0
        }

    print("Returned Output:", result_data.get("output"))

    return jsonify(result_data)


# ======================================================
# RUN SERVER
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)