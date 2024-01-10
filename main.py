# -*- coding: utf-8 -*-
# Python 3

import time

import discord
from discord import app_commands

# Get poker_cards module
from poker_cards import Deck, Hands

# Get Discord token and channel ID
from config import TOKEN, CHANNEL_ID

# Discord client initialization
intents = discord.Intents.default()
client = discord.Client(intents=intents)
slash = app_commands.CommandTree(client)

# Global variables
players = {}
games = {}

game_time = 600

class game:
    def __init__(self, id):
        global players
        self.pid = id
        self.pbet = players[id].default_bet
        self.pchange = [False for _ in range(5)]

        # initialization of deck
        self.deck = Deck()
        self.deck.shuffle()

        # initialization of hand
        self.phand = Hands([self.deck.draw() for _ in range(5)])
        self.bhand = Hands([self.deck.draw() for _ in range(5)])

        # initialize bet
        players[id].bet(self.pbet)

        # 10 minutes timer start
        self.start_time = time.time()
    
    def __repr__(self):
        return "Game: {}".format(self.pid)
    
    def __str__(self):
        return "Game: {}".format(self.pid)

    def bet(self, bet):
        global players
        players[self.pid].bet(bet - self.pbet)
        self.pbet = bet
        return self.pbet

    def add(self, card):
        self.pchange[card] = True
        return self.pchange[card]

    def remove(self, card):
        self.pchange[card] = False
        return self.pchange[card]

    def change(self, card):
        self.phand.cards[card] = self.deck.draw()
        return self.phand.cards[card]
    
    def judge(self):
        if self.phand.hand == self.bhand.hand:
            for i in range(5):
                if int(100 if self.phand.ranks[i] == 1 else self.phand.ranks[i]) > int(100 if self.bhand.ranks[i] == 1 else self.bhand.ranks[i]):
                    self.win()
                    return self.calc_inmoney()
                elif int(100 if self.phand.ranks[i] == 1 else self.phand.ranks[i]) < int(100 if self.bhand.ranks[i] == 1 else self.bhand.ranks[i]):
                    self.lose()
                    return -1
            else:
                self.draw()
                return -2
        elif int(self.phand.hand[0]) > int(self.bhand.hand[0]):
            self.win()
            return self.calc_inmoney()
        else:
            self.lose()
            return -1
    
    def win(self):
        global players
        inmoney = self.calc_inmoney()
        players[self.pid].win(inmoney)
        return players[self.pid].money
    
    def draw(self):
        global players
        players[self.pid].money += self.pbet
        return players[self.pid].money

    def lose(self):
        global players
        players[self.pid].lose()
        return players[self.pid].money

    def calc_inmoney(self):
        base = self.pbet
        return base * 5


class player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.money = 1000
        self.default_bet = 10
        self.win_count = 0
        self.lose_count = 0
    
    def is_bet(self, bet):
        if self.money >= bet:
            return True
        else:
            return False

    def win(self, inmoney):
        self.money += inmoney
        self.win_count += 1
        return self.money

    def lose(self):
        self.lose_count += 1
        return self.money

    def bet(self, bet: int):
        self.money -= bet
        return self.money


def is_game_already(id):
    global games
    if id in games: return True
    else: return False

def is_player_already(id):
    global players
    if id in players: return True
    else: return False


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="On Ready, Use /pkstart"))
    await client.get_channel(CHANNEL_ID).send("on ready !!")
    await slash.sync()


# PLAYER COMMANDs
@slash.command(name="pkregistar", description="ポーカーのプレイヤー登録をします")
async def pkregistar_command(interaction: discord.Interaction):
    global players
    uid = interaction.user.id
    if is_player_already(uid):
        await interaction.response.send_message("既にプレイヤー登録されています")
        return
    players[uid] = player(uid, interaction.user.name)
    msg = "プレイヤー登録が完了しました\n詳細は`/pkstatus`コマンドを参照してください\n```NAME: {}\nID: {}```".format(players[uid].name, players[uid].id)
    await interaction.response.send_message(msg)


@slash.command(name="pkstatus", description="プレイヤーのステータスを表示します")
async def pkstatus_command(interaction: discord.Interaction):
    global players
    uid = interaction.user.id
    if not is_player_already(uid):
        await interaction.response.send_message("プレイヤー登録がされていません\n先に`/pkregistar`コマンドで登録してください")
        return
    msg = "```NAME: {}".format(players[uid].name)
    msg += "\nID: {}".format(players[uid].id)

    msg += "\n\nMONEY: {}".format(players[uid].money)
    msg += "\nDEFAULT BET: {}".format(players[uid].default_bet)

    msg += "\n\nWIN: {}".format(players[uid].win_count)
    msg += "\nLOSE: {}".format(players[uid].lose_count)

    if uid in games.keys():
        msg += "\n\nGAME: {}```".format(games[uid])
    else:
        msg += "```"

    await interaction.response.send_message(msg)

@slash.command(name="pksetbet", description="ポーカーの初期ベットを設定します")
async def pksetbet_command(interaction: discord.Interaction, bet: int):
    global players
    uid = interaction.user.id
    if not is_player_already(uid):
        await interaction.response.send_message("プレイヤー登録がされていません\n先に`/pkregistar`コマンドで登録してください")
        return
    if bet < 10:
        await interaction.response.send_message("ベット額は10以上にしてください")
        return
    players[uid].default_bet = bet
    msg = "初期ベットを設定しました\n```DEFAULT BET: {}```".format(players[uid].default_bet)
    await interaction.response.send_message(msg)


# GAME COMMANDs
@slash.command(name="pkstart", description="ポーカーのボットゲームを開始します")
async def pkstart_command(interaction: discord.Interaction):
    global players, games

    # 10 minutes timer
    delete_list = []
    for i in games.keys():
        if time.time() - games[i].start_time > game_time:
            delete_list.append(i)
            user = await client.fetch_user(i)
            await user.send("終了時刻を超えたので，ゲームが終了しました") # send DM
    for i in delete_list:
        games.pop(i)

    uid = interaction.user.id
    if not is_player_already(uid):
        await interaction.response.send_message("プレイヤー登録がされていません\n先に`/pkregistar`コマンドで登録してください")
        return
    if is_game_already(uid):
        await interaction.response.send_message("既にゲームが開始されています")
        return
    if not players[uid].is_bet(players[uid].default_bet):
        await interaction.response.send_message("所持金が足りません")
        return

    games[uid] = game(uid)

    hand = games[uid].phand
    msg = "ゲームを開始します -- 終了時刻: {}".format(time.ctime(games[uid].start_time + game_time))
    msg += "\nあなたのカード:\n```{}\n--->  {}```".format(str(hand).replace('[', '').replace(']', ''), hand.hand)
    msg += "```\nベット額: {}\n残金: {}```".format(players[uid].default_bet, players[uid].money)
    msg += "\n`/pkbet` : ベットします"
    msg += "\n`/pkadd` : カードを変更キューに追加します - カードの指定子は左から1, 2, 3, 4, 5です"
    msg += "\n`/pkremove` : カードを変更キューから取り消します - カードの指定子は左から1, 2, 3, 4, 5です"
    msg += "\n`/pkchange` : カードを変更して勝負します"
    await interaction.response.send_message(msg)


@slash.command(name="pkbet", description="ポーカーのベットをします")
async def pkbet_command(interaction: discord.Interaction, bet: int):
    global players, games
    uid = interaction.user.id
    if not is_game_already(uid):
        await interaction.response.send_message("ゲームが開始されていません\n先に`/pkstart`コマンドでゲームを開始してください")
        return
    if not players[uid].is_bet(bet):
        await interaction.response.send_message("所持金が足りません")
        return
    if bet < players[uid].default_bet:
        await interaction.response.send_message("ベット額は初期ベット額({}) 以上にしてください".format(players[uid].default_bet))
        return
    games[uid].bet(bet)
    msg = "ベットが完了しました\n```ベット額: {}\n残金: {}```".format(bet, players[uid].money)
    await interaction.response.send_message(msg)


@slash.command(name="pkadd", description="カードを変更キューに追加します")
async def pkadd_command(interaction: discord.Interaction, card: int):
    global players, games
    uid = interaction.user.id
    if not is_game_already(uid):
        await interaction.response.send_message("ゲームが開始されていません\n先に`/pkstart`コマンドでゲームを開始してください")
        return
    if card < 1 or card > 5:
        await interaction.response.send_message("カード番号は1 ~ 5で指定してください")
        return
    games[uid].add(card-1)
    msg = "カード変更を受け付けました\n取り消す場合は，`/pkremove`を使ってください\n```変更するカード: {} #{}\n```".format(games[uid].phand.cards[card-1], card)
    await interaction.response.send_message(msg)


@slash.command(name="pkremove", description="カードを変更キューから取り消します")
async def pkremove_command(interaction: discord.Interaction, card: int):
    global players, games
    uid = interaction.user.id
    if not is_game_already(uid):
        await interaction.response.send_message("ゲームが開始されていません\n先に`/pkstart`コマンドでゲームを開始してください")
        return
    if card < 1 or card > 5:
        await interaction.response.send_message("カード番号は1 ~ 5で指定してください")
        return
    if not games[uid].pchange[card-1]:
        await interaction.response.send_message("そのカードは変更キューに追加されていません")
        return
    games[uid].remove(card-1)
    msg = "カード変更を取り消しました\n```変更を取り消したカード: {} #{}\n```".format(games[uid].phand.cards[card-1], card)
    await interaction.response.send_message(msg)


@slash.command(name="pkshow", description="カードを表示します")
async def pkshow_command(interaction: discord.Interaction):
    global players, games
    uid = interaction.user.id
    if not is_game_already(uid):
        await interaction.response.send_message("ゲームが開始されていません\n先に`/pkstart`コマンドでゲームを開始してください")
        return
    hand = games[uid].phand
    msg = "カードを表示します\n```あなたのカード:\n{}\n--->  {}```".format(str(hand).replace('[', '').replace(']', ''), hand.hand)
    msg += "\n変更キュー: ```"
    if not any(games[uid].pchange):
        msg += "なし"
    else:
        for i in range(5):
            if games[uid].pchange[i]:
                msg += "{} #{}  ".format(hand.cards[i], i+1)
    msg += "```"
    await interaction.response.send_message(msg)


@slash.command(name="pkchange", description="カードを変更して勝負します")
async def pkchange_command(interaction: discord.Interaction):
    global players, games
    uid = interaction.user.id
    if not is_game_already(uid):
        await interaction.response.send_message("ゲームが開始されていません\n先に`/pkstart`コマンドでゲームを開始してください")
        return
    newhandid = [None for _ in range(5)]
    for i in range(5):
        if games[uid].pchange[i]:
            newhandid[i] = games[uid].deck.draw()
        else:
            newhandid[i] = games[uid].phand.cards[i]
    games[uid].hand = Hands(newhandid)
    hand = games[uid].hand
    msg = "カードを変更しました\n```あなたのカード:\n{}\n--->  {}```".format(str(hand).replace('[', '').replace(']', ''), hand.hand)
    msg += "ボットのカード:\n```{}\n--->  {}```".format(str(games[uid].bhand).replace('[', '').replace(']', ''), games[uid].bhand.hand)
    msg += "\n勝敗: ```\n"
    judge = games[uid].judge()
    print(games[uid].phand.ranks, games[uid].bhand.ranks)
    if judge == -1:
        msg += "LOSE"
    elif judge == -2:
        msg += "DRAW"
    else:
        msg += "WIN\n賞金: {}".format(judge)
    msg += "```"

    games.pop(uid)
    await interaction.response.send_message(msg)


client.run(TOKEN)


"""
@tree.command(name="test",description="テストコマンドです。")
async def test_command(interaction: discord.Interaction,picture:discord.Attachment):
    embed=discord.Embed(title="画像",color=0xff0000)
    embed.set_image(url=picture.url)#URLでEmbedに画像を貼る
    await interaction.response.send_message(embed=embed)
"""
