from flask import Flask, request, jsonify
from pygdbmi.gdbcontroller import GdbController
from flask_cors import CORS
import subprocess
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# Initialize global variables to store the GDB controller and program name
gdb_controller = None
program_name = None

def execute_gdb_command(command):
    # Execute the provided command using the GDB controller
    response2 = gdb_controller.write(command)
    if response2 is None:
        raise RuntimeError("No response from GDB controller")
    
    # Extracting the 'message' field from the response
    # response=jsonify(response2)
    # print(type(response2))
    strm=""
    for rem in response2:
        # print(rem)
        strm=strm+"\n "+str(rem.get('payload'))
    # print(strm)

    return strm.strip()

    # output = "\n".join([elem.get('payload', '') for elem in response2])
    # print(output)
    # return output.strip()

def start_gdb_session(program):
    global gdb_controller, program_name
    program_name = program

    # Initialize the GDB controller
    try:
        gdb_controller = GdbController()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize GDB controller: {e}")

    # Start the GDB session
    try:
        response = gdb_controller.write(f"-file-exec-and-symbols {program_name}.exe")
        if response is None:
            print("No response from GDB controller")
            raise RuntimeError("No response from GDB controller")
    except Exception as e:
        print("Failsed")
        raise RuntimeError(f"Failed to set program file: {e}")

    # Start running the program
    try:
        response = gdb_controller.write("run")
        if response is None:
            raise RuntimeError("No response from GDB controller")
    except Exception as e:
        raise RuntimeError(f"Failed to start program: {e}")

@app.route('/gdb_command', methods=['POST'])
def gdb_command():
    global program_name
    data = request.get_json()
    command = data.get('command')
    file = data.get('name')
    print(command)
    
    # Start the GDB session if not already started
    if program_name!=file:
        print(file)
        print(program_name)
        start_gdb_session(f'{file}')

    try:
        # Execute the GDB command
        result = execute_gdb_command(command)
        response = {
            'success': True,
            'result': result,
            'code': f"execute_gdb_command('{command}')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': f"execute_gdb_command('{command}')"
        }
    
    return jsonify(response)

@app.route('/compile', methods=['POST'])
def compile_code():
    global program_name
    data = request.get_json()
    code = data.get('code')
    name = data.get('name')

    # Write code to a temporary file
    with open(f'{name}.cpp', 'w') as file:
        file.write(code)

    # Compile the code
    result = subprocess.run(['g++', f'{name}.cpp', '-o', f'{name}.exe'], capture_output=True, text=True)

    if result.returncode == 0:
        program_name=None
        return jsonify({'success': True, 'output': 'Compilation successful.'})
    else:
        return jsonify({'success': False, 'output': result.stderr})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
