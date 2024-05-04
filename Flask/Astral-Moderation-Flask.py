from flask import Flask, render_template, Response
import subprocess
import time
import threading

app = Flask(__name__)

def execute_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    command_output, command_error = process.communicate()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    execute_command(['/home/ryzenfox/Astral-Moderation-v2/pythonvenv/python3.11.2-astral/bin/python', '/home/ryzenfox/Astral-Moderation-v2/bot.py'])
    return 'Bot started successfully'

@app.route('/stop')
def stop():
    execute_command(['pkill', '-f', 'bot.py'])
    return 'Bot stopped successfully'

@app.route('/restart')
def restart():
    execute_command(['pkill', '-f', 'bot.py'])
    time.sleep(5)
    execute_command(['/home/ryzenfox/Astral-Moderation-v2/pythonvenv/python3.11.2-astral/bin/python', '/home/ryzenfox/Astral-Moderation-v2/bot.py'])
    return 'Bot restarted successfully'

@app.route('/gitpull')
def gitpull():
    execute_command(['pkill', '-f', 'bot.py'])
    time.sleep(2)
    execute_command(['git', '-C', '/home/ryzenfox/Astral-Moderation-v2', 'pull'])
    time.sleep(5)
    execute_command(['/home/ryzenfox/Astral-Moderation-v2/pythonvenv/python3.11.2-astral/bin/python', '/home/ryzenfox/Astral-Moderation-v2/bot.py'])
    return 'Main branch sync and bot restart completed successfully'

@app.route('/systemrestart')
def systemrestart():
    execute_command(['sudo', 'systemctl', 'reboot'])
    return 'System is restarting'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6040, debug=True)
