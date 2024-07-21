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
    subprocess.Popen(['/usr/share/pythonvenv/python3.11.2-astral+flask-linux/bin/python', '/home/ryzenfox/Astral-Moderation-v2/bot.py'], cwd='/home/ryzenfox/Astral-Moderation-v2/')
    time.sleep(7)
    print("Bot started successfully")
    return 'Bot started successfully'

@app.route('/stop')
def stop():
    os.system('pkill -f bot.py')
    print("Bot stopped successfully")
    return 'Bot stopped successfully'

@app.route('/restart')
def restart():
    os.system('pkill -f bot.py')
    start()
    print("Bot restarted successfully")
    return 'Bot restarted successfully'

@app.route('/gitpull')
def gitfetch():
    os.system('pkill -f bot.py')
    os.system('git -C /home/ryzenfox/Astral-Moderation-v2/ pull')
    start()
    print("Main branch sync and bot restart completed successfully; Flask changes won't take effect until a script restart")
    return "Main branch sync and bot restart completed successfully; Flask changes won't take effect until a script restart"

@app.route('/systemrestart')
def systemrestart():
    os.system('sudo systemctl reboot')
    print("System is restarting")
    return 'System is restarting'

@app.route('/systemshutdown')
def systemshutdown():
    os.system('sudo systemctl poweroff')
    print("System is shutting down")
    return 'System is shutting down'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6040, debug=False)