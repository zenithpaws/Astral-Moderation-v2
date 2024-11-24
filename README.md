# Discord Bot

A powerful and customizable Discord bot built with [Nextcord](https://github.com/nextcord/nextcord) and integrated with Firestore for persistent data storage. This bot includes features for moderation, utility commands, and automated server management.

---

## Features

- **Moderation Tools:** Manage bans, kicks, warns, and mutes.
- **Utility Commands:** Announcements, message purging, role management, and more.
- **Automated Events:** Welcome and leave messages with configurable settings.
- **Persistent Configuration:** Store roles, channels, and settings in Firestore.
- **Slash Command Support:** Modern and user-friendly Discord commands.

---

## Setup and Configuration

### Prerequisites

1. **Python 3.8+**
   - Download and install Python from [python.org](https://www.python.org/).

2. **Dependencies**
   - Install all required libraries using:
     ```bash
     pip install -r requirements.txt
     ```

3. **Firebase Project**
   Follow these steps to set up your Firestore database:

   #### Step 1: Create a Firebase Project
   - Go to the [Firebase Console](https://console.firebase.google.com/).
   - Click on **"Add Project"**.
   - Enter a name for your project and follow the setup steps.
   - Once created, navigate to your project dashboard.

   #### Step 2: Enable Firestore Database
   - In the Firebase Console, click on **"Build"** in the left sidebar, then select **"Firestore Database"**.
   - Click **"Create Database"** and follow the prompts.
   - Choose **Production Mode** for security or **Test Mode** for easier initial setup.

   #### Step 3: Generate Admin SDK Credentials
   - Go to **"Project Settings"** in the Firebase Console (click the gear icon in the top left).
   - Navigate to the **"Service Accounts"** tab.
   - Click **"Generate New Private Key"**. This will download a JSON file containing your Firebase Admin SDK credentials.
   - Rename this file to `firebase.json` and place it in the root directory of your project.

   #### Step 4: Set Up Firestore Collections
   - In the Firestore database, create the following collections and documents to store bot settings:
     1. **Collection:** `secrets`
        - Document: `bot_token`
          - Field: `token` (String) → Add your bot token here.
        - Document: `server_invite` *(Optional)*
          - Field: `link` (String) → Add your server invite link.
        - Document: `github_repo` *(Optional)*
          - Field: `link` (String) → Add your GitHub repository link.
     2. **Collection:** `roles`
          - Document: `allowed_commands`
            - Field: `examplerole1` (Boolean) → true
            - Field: `examplerole2` (Boolean) → true

   #### Step 3: Test Your Firebase Connection
   - Ensure the `firebase.json` file is accessible in your bot directory.
   - The bot will automatically connect to Firestore when run if the credentials are valid.

---

### Bot Setup

1. **Clone or Download**
   ```bash
   git clone https://github.com/zenithpaws/Astral-Moderation-v2
   cd Astral-Moderation-v2


2. **Add Firebase Credentials**
   Place your `firebase.json` file in the root directory of the project.

3. **Configure Firestore**
   - Add the following keys to the Firestore database under the collection `secrets`:
     - `bot_token`: Your bot token from the Discord Developer Portal.
     - `server_invite` (optional): Your server's invite link.
     - `github_repo` (optional): A link to your bot's GitHub repository.

4. **Run the Bot**
   Execute the bot using:
   ```bash
   python bot.py
   ```

---

## Usage

### Slash Commands

The bot supports a wide range of slash commands. Below are some highlights:

#### Moderation
- `/ban [member] [reason]` - Ban a user.
- `/kick [member] [reason]` - Kick a user.
- `/warn [member] [reason]` - Issue a warning to a user.
- `/mute [member]` - Mute a user.
- `/unmute [member]` - Unmute a user.

#### Configuration
- `/setwarnthreshold [number]` - Set the warning threshold.
- `/setmuterole [role]` - Assign a role to muted members.
- `/setjoinchannel [channel]` - Specify the channel for welcome messages.

#### Utility
- `/purge [amount]` - Delete messages in a channel.
- `/invite` - Retrieve the server's invite link.

#### General
- `/help` - View a list of all available commands.

---

## Directory Structure

```plaintext
.
├── bot.py                # Main bot script
├── firebase.json         # Firebase Admin SDK credentials
├── requirements.txt      # Python dependencies
├── Flask/
│   └── pid.txt           # Stores the PID of the running bot
```

---

## Requirements

Install dependencies by running:
```bash
pip install -r requirements.txt
```

---

## Contributing

Feel free to fork the repository, submit issues, or create pull requests. Contributions are always welcome!

---

## License

This project is licensed under the MIT License.

## Additonal Notes

* Only setup the collections and documents in these instructions, any other fields that will be needed are created when you set them using the bot's commands
* When setting up the `allowed_commands` document in `roles` collection, don't  specifiy roles that shouldn't be allowed to run commands, only specifiy the roles that **should**
