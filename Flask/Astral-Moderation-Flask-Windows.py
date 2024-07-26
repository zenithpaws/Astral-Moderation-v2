import os
import subprocess
import flask
import firebase_admin
import time
import logging
import psutil
from flask import Flask, render_template, jsonify
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Set up logging to suppress the spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARN)  # Only show warnings, not requests

# Initialize Firebase
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Global variables to keep track of network stats
previous_net_io = psutil.net_io_counters()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    subprocess.Popen(['C:/Users/furio/OneDrive/Documents/GitHub/Astral-Moderation-v2/pythonvenv/python3.12.2-astral+flask-windows/Scripts/python.exe', 'C:/Users/furio/OneDrive/Documents/GitHub/Astral-Moderation-v2/bot.py'], cwd='C:/Users/furio/OneDrive/Documents/GitHub/Astral-Moderation-v2/')
    time.sleep(7)
    print("Bot started successfully")
    return 'Bot started successfully'

@app.route('/stop')
def stop():
    with open('pid.txt', 'r') as file:
        pid = int(file.read())
    os.system(f'taskkill /f /pid {pid}')
    print("Bot stopped successfully")
    return 'Bot stopped successfully'

@app.route('/restart')
def restart():
    with open('pid.txt', 'r') as file:
        pid = int(file.read())
    os.system(f'taskkill /f /pid {pid}')
    start()
    print("Bot restarted successfully")
    return 'Bot restarted successfully'

@app.route('/gitpull')
def gitfetch():
    stop()
    os.system('git -C C:/Users/furio/OneDrive/Documents/GitHub/Astral-Moderation-v2/ pull')
    start()
    print("Main branch sync and bot restart completed successfully; Flask changes won't take effect until a script restart")
    return "Main branch sync and bot restart completed successfully; Flask changes won't take effect until a script restart"

@app.route('/systemrestart')
def systemrestart():
    os.system('shutdown -r -t 0')
    print("System is restarting")
    return 'System is restarting'

@app.route('/systemshutdown')
def systemshutdown():
    os.system('shutdown -s -t 0')
    print("System is shutting down")
    return 'System is shutting down'

# Define network rate functions
last_upload = 0
last_download = 0

def get_network_upload_rate():
    global last_upload
    net_io = psutil.net_io_counters()
    upload_rate = (net_io.bytes_sent - last_upload) / 1024 / 1024  # Convert to MB
    last_upload = net_io.bytes_sent
    return upload_rate

def get_network_download_rate():
    global last_download
    net_io = psutil.net_io_counters()
    download_rate = (net_io.bytes_recv - last_download) / 1024 / 1024  # Convert to MB
    last_download = net_io.bytes_recv
    return download_rate

@app.route('/systemstatus', methods=['GET'])
def system_status():
    return jsonify({
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_used': psutil.disk_usage('/').percent,
        'network_upload': get_network_upload_rate(),
        'network_download': get_network_download_rate()
    })

@app.route('/firebasedata', methods=['GET'])
def firebase_data():
    try:
        # Fetch settings
        settings_ref = db.collection('command_configuration')
        join_message = settings_ref.document('join_message').get().to_dict().get('message', 'N/A')
        leave_message = settings_ref.document('leave_message').get().to_dict().get('message', 'N/A')
        logging_enabled = settings_ref.document('logging').get().to_dict().get('boolean', 'N/A')
        warn_threshold = settings_ref.document('warn_threshold').get().to_dict().get('value', 'N/A')
        
        # Fetch warnings
        warnings_ref = db.collection('data').document('warns').get().to_dict()
        warnings_count = 0
        if warnings_ref:
            for user_id, warns in warnings_ref.items():
                warnings_count += len(warns)  # Count the total number of warnings
        
        # Fetch bans
        bans_ref = db.collection('data').document('bans').get().to_dict()
        bans_count = len(bans_ref) if bans_ref else 0
        
        return jsonify({
            'settings': {
                'join_message': join_message,
                'leave_message': leave_message,
                'logging': logging_enabled,
                'warn_threshold': warn_threshold
            },
            'warnings': warnings_count,
            'bans': bans_count
        })
    except Exception as e:
        print(f"Error fetching Firebase data: {e}")
        return jsonify({
            'settings': {},
            'warnings': 0,
            'bans': 0
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6040, debug=False)