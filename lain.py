# coding: UTF-8
# https://discordpy.readthedocs.io/ja/latest/index.html
# https://qiita.com/sizumita/items/9d44ae7d1ce007391699
# https://qiita.com/Lazialize/items/81f1430d9cd57fbd82fb 
# https://qiita.com/Shirataki2/items/3b9f9766bc25bb204ed3
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
from discord.ext.commands.errors import (
    BadArgument,
    TooManyArguments,
    MissingRequiredArgument
)
import logging

# cogs
import traceback

# spllite3
import sqlite3

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

INITIAL_EXTENSIONS = [
    'cogs.feed'
]

class Lain(commands.Bot):

    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)
        
        self.sqlite3 = sqlite3.connect("lain.db")

        # INITIAL_COGSに格納されている名前から、コグを読み込む。
        # エラーが発生した場合は、エラー内容を表示。
        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
    
    def __del__(self):
        self.sqlite3.close()
    
    def make_categories_list(self, guild):
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

    def get_all_text_channels(self, guild):
        # 以下のような形式で現在存在する全てのテキストチャンネルを返す
        # {'テキストチャンネル': ['intro', 'freedom', 'gamers', 'feeds', 'learning-python', 'windows']}
        current_all_text_channels = {}
        for channel in guild.text_channels:
            if not channel.category.name in current_all_text_channels.keys():
                current_all_text_channels[channel.category.name] = [channel.name]
            else:
                current_all_text_channels[channel.category.name].append(channel.name)
        return current_all_text_channels

    def category_name2category_id(self, guild, category_name):
        # カテゴリ名からカテゴリIDを返す
        for category in guild.categories:
            if category_name == category.name:
                return category.id
        return False

    def get_lain_channel(self, guild):
        for channel in guild.text_channels:
            if channel.category.name == 'LAIN' and channel.name == 'lain':
                return channel

    async def lain_loggin(self, channel):
        now = datetime.datetime.now()
        await channel.send("[lain@wired]$ log in at {}".format(now.strftime("%Y/%m/%d %H:%M:%S.%f")))

    async def on_ready(self):
       print('Logged on as {0}!'.format(self.user))
       
       for guild in self.guilds:
           # 参加しているギルド全てにおいて必要なカテゴリを作成する
           for c in self.make_categories_list(guild):
               await guild.create_category(c, overwrites=None, reason=None)
           # 参加しているギルド全てにおいて必要なテキストチャンネルを作成する
           # {'テキストチャンネル': ['intro', 'freedom', 'gamers', 'feeds', 'learning-python', 'windows']}
           current_all_text_channels = self.get_all_text_channels(guild)
           # 参加しているギルド全てにおいて必要なチャンネルを作成する
           for need_category in need_channels.keys():
               if not need_category in current_all_text_channels.keys():
                   current_all_text_channels[need_category] = []
               set_need = set(need_channels[need_category])
               set_current = set(current_all_text_channels[need_category])
               make_channel_list = set_need - set_current
               for make_channel in make_channel_list:
                   category_id = self.category_name2category_id(guild, need_category)
                   category = guild.get_channel(category_id)
                   await category.create_text_channel(make_channel)
           # この時点で絶対に存在するLAINカテゴリのlainチャンネルを取得する
           lain_channel = self.get_lain_channel(guild)
           await self.lain_loggin(lain_channel)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, BadArgument):
            return await ctx.send(error)
        if isinstance(error, MissingRequiredArgument):
            return await ctx.send(error)
        if isinstance(error, TooManyArguments):
            return await ctx.send(error)

if __name__ == '__main__':
    # botインスタンスの作成
    lain = Lain(command_prefix='!ain ')
    # botの起動
    lain.run(DISCORD_BOT_TOKEN)

