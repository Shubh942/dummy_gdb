import asyncio
import threading
from flask import Flask, request, jsonify
import asyncio.subprocess

app = Flask(__name__)

# Initialize global variables to store the GDB subprocess and program name
gdb_process = None
program_name = None
lock = threading.Lock()
output_queue = asyncio.Queue()

def start_gdb_session(program):
    global gdb_process, program_name
    with lock:
        program_name = program
        # Start the GDB subprocess
        gdb_process = asyncio.create_subprocess_exec('gdb', '--interpreter=mi', program_name,
                                                     stdin=asyncio.subprocess.PIPE,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        asyncio.ensure_future(read_output())

async def read_output():
    global gdb_process
    while True:
        line = await gdb_process.stdout.readline()
        if line.strip() == b"(gdb)":
            await output_queue.put(line)
        else:
            await output_queue.put(line)

async def execute_gdb_command(command):
    global gdb_process
    async with lock:
        # Send command to the GDB subprocess
        gdb_process.stdin.write(command + '\n')
        await gdb_process.stdin.drain()
        # Wait for the GDB prompt
        while True:
            output = await output_queue.get()
            if output.strip() == b"(gdb)":
                break
        # Read the output from the GDB subprocess
        output = b""
        while True:
            line = await output_queue.get()
            if line.strip() == b"(gdb)":
                break
            output += line
        return output.strip()

@app.route('/gdb_command', methods=['POST'])
async def gdb_command():
    data = await request.get_json()
    command = data.get('command')
    
    # Start the GDB session if not already started
    if gdb_process is None:
        await start_gdb_session(data.get('program', 'program.exe'))

    # Execute the GDB command
    try:
        result = await execute_gdb_command(command)
        response = {
            'success': True,
            'result': result.decode('utf-8'),
            'code': f"await execute_gdb_command('{command}')"
        }
    except Exception as e:
        response = {
            'success': False,
            'error': str(e),
            'code': f"await execute_gdb_command('{command}')"
        }
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
