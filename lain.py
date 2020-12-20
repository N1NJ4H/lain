# coding: UTF-8
# https://discordpy.readthedocs.io/ja/latest/index.html
# python3 -m pip install -U discord.py[voice]
# pip install dotenv

# botアカウント作成
# https://discord.com/developers/applications/

# .envを読み込むためのモジュール
import os
from os.path import join, dirname
from dotenv import load_dotenv

# discord関連のモジュール
import discord
from discord.ext import tasks
from discord.ext import commands
import logging
# logger設定
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='lain.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# .envファイルからDiscord Tokenを読み込む
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 

# 必ず作成するチャンネル
need_channels = {
    'Lain': ['Lain', 'Twitter', 'Facebook'], #LainカテゴリにLainチャンネルは必須
    'Feed': []
}
# botインスタンスの作成
bot = commands.Bot(command_prefix='!ain ', help_command=None)

def make_categories_list(guild):
    # 現在ギルドに存在するカテゴリと必要カテゴリを比較して、
    # 作成すべきカテゴリのリストを返す
    current_all_categories = []
    make_categories = []
    for category in guild.categories:
        current_all_categories.append(category.name)
    for need_category in need_channels.keys():
        if not need_category in current_all_categories:
            make_categories.append(need_category)
    return make_categories

def get_all_text_channels(guild):
    # 以下のような形式で現在存在する全てのテキストチャンネルを返す
    # {'テキストチャンネル': ['intro', 'freedom', 'gamers', 'feeds', 'learning-python', 'windows']}
    current_all_text_channels = {}
    for channel in guild.text_channels:
        if not channel.category.name in current_all_text_channels.keys():
            current_all_text_channels[channel.category.name] = [channel.name]
        else:
            current_all_text_channels[channel.category.name].append(channel.name)
    return current_all_text_channels

#------------------#
# BOT EVENT METHOD #
#------------------#
@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

    for guild in bot.guilds:
        # 参加しているギルド全てにおいて必要なカテゴリを作成する
        for c in make_categories_list(guild):
            await guild.create_category(c, overwrites=None, reason=None)
        # 参加しているギルド全てにおいて必要なテキストチャンネルを作成する
        # {'テキストチャンネル': ['intro', 'freedom', 'gamers', 'feeds', 'learning-python', 'windows']}
        current_all_text_channels = get_all_text_channels(guild)
        print(current_all_text_channels)





    
    

# botの起動
bot.run(DISCORD_BOT_TOKEN)
