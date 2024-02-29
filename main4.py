from flask import Flask, request, jsonify
from pygdbmi.gdbcontroller import GdbController
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
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
        print(rem)
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
        response = gdb_controller.write(f"-file-exec-and-symbols {program_name}")
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
    
    # Start the GDB session if not already started
    if program_name is None:
        start_gdb_session(data.get('program', 'program.exe'))

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

if __name__ == '__main__':
    app.run(debug=True, port=8000)