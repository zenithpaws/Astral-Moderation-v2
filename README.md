# Discord Moderation Bot

This is a Discord moderation bot built using [nextcord](https://nextcord.dev/) (formerly known as discord.py) and [Cloud Firestore](https://firebase.google.com/products/firestore) for data storage.

## Features

- Ban, unban, and kick members from the server.
- Warn members and keep track of warnings.
- View warnings for the server and individual members.
- Clear warnings for members.
- Set the warn threshold and punishment for crossing the threshold.
- Mute and unmute members to manage their ability to send messages.
- Lock and unlock channels to control message sending permissions.
- Purge messages from channels.
- Add and remove roles from members.
- Set and toggle the logging channel.
- Make announcements.
- Get and set the server invite link.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/zenithpaws/Ryzen-Moderation-v2
   ```

# Discord Bot and Firebase Setup Guide

This guide provides detailed instructions for setting up a Discord bot with [nextcord](https://nextcord.dev/) and integrating it with [Cloud Firestore](https://firebase.google.com/products/firestore) for data storage.

## Discord Bot Setup

### 1. Create a Discord Bot Account:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click on "New Application" to create a new application.
3. Enter a name for your application (this will be your bot's name).
4. Once created, go to the "Bot" tab on the left sidebar.
5. Click on "Add Bot" to create a bot user for your application.
6. Customize your bot's settings (e.g., profile picture, username).

### 2. Get the Bot Token:

1. After creating the bot, you'll see a "Token" section under the bot username.
2. Click on "Copy" to copy the token. This token is used to authenticate your bot with Discord.

### 3. Add the Bot to Your Discord Server:

1. Still in the Discord Developer Portal, go to the "OAuth2" tab.
2. Under the "OAuth2 URL Generator" section, select the bot scope.
3. Select the permissions your bot needs (e.g., "Send Messages", "Read Message History", "Manage Messages" for a moderation bot).
4. Copy the generated OAuth2 URL and paste it into your web browser.
5. Select the server where you want to add the bot and authorize it.

### 4. Install Required Packages:

You'll need to install the required Python packages to interact with Discord and Firebase.

```
import nextcord
import firebase_admin
from nextcord.ext import commands
from firebase_admin import credentials, firestore
from enum import Enum
```

### 5. Set Up Bot Code:

Replace `"YOUR_BOT_TOKEN"` in your bot code with the actual bot token you obtained earlier.

### 6. Run Your Bot:

Run your bot script using Python. If everything is set up correctly, your bot should connect to Discord and appear online in your server.

### Additional Tips:

- **Permissions**: Make sure your bot has the necessary permissions in your Discord server to perform its intended actions.
- **Testing**: Test your bot thoroughly in a development environment before deploying it to a production server.
- **Error Handling**: Implement error handling to gracefully handle failures and exceptions in your bot code.
- **Security**: Keep your bot token and other sensitive information secure. Avoid sharing them publicly or hardcoding them in your code.

## Firebase Setup

### 1. Set Up a Firebase Project:

1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. Follow the prompts to set up your project.

### 2. Add Firebase to Your Web App:

1. In the Firebase Console, go to your project settings.
2. Under the "General" tab, scroll down to "Your apps" and click on the "</>" icon to add a new web app.
3. Follow the instructions to register your app and obtain your Firebase configuration.

### 3. Set Up Firestore Database:

1. In the Firebase Console, go to the "Firestore Database" section.
2. Create a new Firestore database.
3. Start in test mode for now and adjust permissions as needed for production.

### 4. Authentication (Optional):

You can set up authentication methods such as email/password, Google, Facebook, etc., depending on your bot's requirements.

### 5. Use Firebase Admin SDK in Your Bot Code:

Integrate Firebase into your bot code using the Firebase Admin SDK to read from and write to Firestore.

### 6. Deploy Your Bot:

Deploy your bot to a server or hosting service where it can run continuously and interact with Discord and Firebase.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
