# coding: UTF-8
# https://discordpy.readthedocs.io/ja/latest/index.html
# https://qiita.com/sizumita/items/9d44ae7d1ce007391699
# https://qiita.com/Lazialize/items/81f1430d9cd57fbd82fb 
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

# feed関連のモジュール
import sqlite3
import feedparser

# その他のモジュール
import datetime

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

# 以下の値はKEYはカテゴリに対応し、値はチャンネルに対応する
# カテゴリは大文字で記載し、チャンネル名は小文字で記載する必要がある
need_channels = {
    'LAIN': ['lain'], #LainカテゴリにLainチャンネルは必須
    'FEED': [],
}

#-----------------------#
# FEED related function #
#-----------------------#

sql_create_feed_info_tbl = '''
CREATE TABLE IF NOT EXISTS feed_info (
	feed_title text PRIMARY KEY,
	url UNIQUE,
    channel_id int
)
'''

sql_create_feed_entry_tbl = '''
CREATE TABLE IF NOT EXISTS feed_entry (
	id text PRIMARY KEY,
    title text,
    url text,
    timestamp timestamp
)
'''

def sqlite3_connect():
    conn = sqlite3.connect("lain.db")
    return conn

def sqlite3_maintenance():
    conn = sqlite3_connect()
    # FEED_INFOテーブルの作成
    conn.execute(sql_create_feed_info_tbl)
    # FEED_ENTRYテーブルの作成
    conn.execute(sql_create_feed_entry_tbl)
    # 不要なエントリの削除
    # 未実装
    conn.close()

#--------------------------#
# Discord related function #
#--------------------------#
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

def category_name2category_id(guild, category_name):
    # カテゴリ名からカテゴリIDを返す
    for category in guild.categories:
        if category_name == category.name:
            return category.id
    return False

def get_lain_channel(guild):
    for channel in guild.text_channels:
        if channel.category.name == 'LAIN' and channel.name == 'lain':
            return channel

async def lain_loggin(channel):
    now = datetime.datetime.now()
    await channel.send("[lain@wired]$ log in at {}".format(now.strftime("%Y/%m/%d %H:%M:%S.%f")))

# botインスタンスの作成
bot = commands.Bot(command_prefix='!ain ', help_command=None)
# sqllite3メンテナンス
sqlite3_maintenance()

#--------------------#
# BOT COMMAND METHOD #
#--------------------#
@bot.command()
async def feed(ctx, channel_name, url):
    feeds = feedparser.parse(url)
    feed_title = feeds.feed.title
    await ctx.send('FEED_TITLE {}'.format(feed_title))

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
        # 参加しているギルド全てにおいて必要なチャンネルを作成する
        for need_category in need_channels.keys():
            if not need_category in current_all_text_channels.keys():
                current_all_text_channels[need_category] = []
            set_need = set(need_channels[need_category])
            set_current = set(current_all_text_channels[need_category])
            make_channel_list = set_need - set_current
            for make_channel in make_channel_list:
                category_id = category_name2category_id(guild, need_category)
                category = guild.get_channel(category_id)
                await category.create_text_channel(make_channel)
        # この時点で絶対に存在するLAINカテゴリのlainチャンネルを取得する
        lain_channel = get_lain_channel(guild)
        await lain_loggin(lain_channel)

# botの起動
bot.run(DISCORD_BOT_TOKEN)
