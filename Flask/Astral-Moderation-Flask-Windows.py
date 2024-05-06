import os
from flask import Flask, render_template
import subprocess
import time

app = Flask(__name__)

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
def gitpull():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6040, debug=False)