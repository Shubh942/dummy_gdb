from flask import Flask, request, jsonify
import subprocess
import time


app = Flask(__name__)

# Initialize global variables to store the GDB subprocess and program name
gdb_process = None
program_name = None

def execute_gdb_command(command):
    global gdb_process
    # Send command to the GDB subprocess
    
    gdb_process.stdin.write(command + '\n')
    gdb_process.stdin.flush()
    # Read the output from the GDB subprocess
    output = ""
    while True:
        line = gdb_process.stdout.readline().strip()
        
        if line == "(gdb)":
            break
        output += line + "\n"
    return output.strip()

def start_gdb_session(program):
    global gdb_process, program_name
    program_name = program
    # Start the GDB subprocess
    gdb_process = subprocess.Popen(['gdb', '--interpreter=mi', program_name],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
    
    # Wait for GDB prompt
    while True:
        line = gdb_process.stdout.readline().strip()
        if line == "(gdb)":
            break
        time.sleep(0.1)  # Adjust the sleep time as needed

    # Send a continue command to ensure the program starts running
    execute_gdb_command("c")

@app.route('/gdb_command', methods=['POST'])
def gdb_command():
    global gdb_process, program_name
    data = request.get_json()
    command = data.get('command')
    print(command)
    
    # Start the GDB session if not already started
    if gdb_process is None:
        start_gdb_session(data.get('program', 'program.exe'))

    # Execute the GDB command
    print("hello")
    try:
        result2=""
        if command=='run':
            result = execute_gdb_command(command)
            result2 = execute_gdb_command(command)
        else:
            result2 = execute_gdb_command(command)
            
        # result2=jsonify(result)
        response = {
            'success': True,
            'result': result2,
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
