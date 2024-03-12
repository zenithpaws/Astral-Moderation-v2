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

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. [Setup a Firebase account](https://console.firebase.google.com/project/_/firestore/data) and save them as `firebase.json` in the root directory.

4. Set up your Discord bot token and other secrets in Firebase Firestore.

5. Run the bot:

   ```bash
   python bot.py
   ```

## Usage

- Use the provided slash commands in Discord to interact with the bot.
- Ensure that the bot has appropriate permissions in your Discord server.

## Contributing

Contributions are welcome! If you have any ideas for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
