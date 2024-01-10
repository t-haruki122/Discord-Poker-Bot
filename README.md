POKER Bot in Discord
====

A Discord bot of a plain poker game with bot.  
Users can play in text channel, using slash(/) command.

## Description
Try this bot easily:
[Invite Bot](https://discord.com/api/oauth2/authorize?client_id=1194633103218593882&permissions=551903299584&scope=bot)

## Requirement
 - Python 3  
 - Discord Account
 - Discord V2 (Python Library)
```
 $ pip install discord
```

## Usage
### 0. Launch Bot (For Dev)
1. Confirm Discord Library is already installed.
2. Open `Config.py` and edit `TOKEN` and `CHANNEL_ID`. (*1)
3. Launch Terminal and move Discord-Poker-Bot directory.
4. Execute Bot Server.
```
 $ python main.py
```

### 1. Registar (For User)
Create your poker account and check the information.
1. Use `/pkregistar` to create your Poker Account.
2. Use `/pkstatus` to check your information.
3. Use `/pksetbet` to set initial bet amount.

### 2. Play Game (For User)
Start Poker Game (Time Limit: 10 minutes)
1. Use `/pkstart` to start game
2. Use `/pkbet` to decide your bet amount.
3. Look Hands and decide cards to replace.  
  2-1. Use `/pkadd` to add card to replace queue.  
  2-2. Use `/pkremove` to remove card from replace queue.  
  2-3. Use `/pkshow` to check cards information.
4. Repeat 2 and confirm all replace card are in queue.  
5. Use `/pkchange` to open a cards.

### (*1) How To Get TOKEN and CHANNEL_ID?  
##### TOKEN:
1. Access [Discord Developer Portal](discord.com/developers/).
2. Click `New Application` and enter name like `POKERBOT`.
3. Move to `Bot` and Click `Reset Token`.
4. The Revealed String is your bot Token.

##### CHANNEL_ID:
1. Open Discord Client.
2. Open `settings` and move to `Advanced`.
3. Enable `Developer Mode`.
4. Go back to chat screen and right click any channel.
5. Click `Copy Channel ID`.


## Reference
- [discord.py](https://discordpy.readthedocs.io/ja/latest/)
- [遊びかた：ポーカー - NINTENDO](https://www.nintendo.co.jp/others/playing_cards/howtoplay/poker/index.html)

## Author
[t-haruki122](https://github.com/t-haruki122)