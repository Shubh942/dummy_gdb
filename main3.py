from flask import Flask, request, jsonify
import gdb

app = Flask(__name__)

# Initialize global variables to store the GDB subprocess and program name
program_name = None

def execute_gdb_command(command):
    # Execute the provided command using gdb.execute
    output = gdb.execute(command, to_string=True)
    return output.strip()

def start_gdb_session(program):
    global program_name
    program_name = program
    # Start the GDB session
    gdb.execute(f"file {program_name}")
    # Start running the program
    gdb.execute("run")

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
