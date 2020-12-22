import discord
from discord.ext import commands
from discord.ext.commands.errors import (
    BadArgument,
    TooManyArguments,
    MissingRequiredArgument
)
# feed関連のモジュール
import feedparser

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
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
'''

class Feed(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # sqllite3メンテナンス
        self.sqlite3_maintenance()

    def sqlite3_maintenance(self):
        # FEED_INFOテーブルの作成
        self.bot.sqlite3.execute(sql_create_feed_info_tbl)
        # FEED_ENTRYテーブルの作成
        self.bot.sqlite3.execute(sql_create_feed_entry_tbl)
        # 不要なエントリの削除
        # 未実装

    @commands.group()
    async def feed(self, ctx):
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send('this command need sub commands')
    
    async def ensure_feed_channel(self, feed_category, feed_channel):
        channel = discord.utils.get(feed_category.channels, name=feed_channel.lower())
        if channel is None:
            channel = await feed_category.create_text_channel(feed_channel.lower())
            return channel.id 
        else:
            return channel.id 

    @feed.command(ignore_extra=False)
    async def add(self, ctx, channel, url):
        feeds = feedparser.parse(url)
        try:
            feed_title = feeds.feed.title
        except:
            await ctx.send('url analyze failed. this url is corret feed url?')
            return False
        feed_category_id = self.bot.category_name2category_id(ctx.guild, 'FEED')
        feed_category = ctx.guild.get_channel(feed_category_id)
        # 指定されたチャンネルを作成し、チャンネルIDを返す
        feed_channel_id = await self.ensure_feed_channel(feed_category, channel)
        feed_channel = ctx.guild.get_channel(feed_channel_id)
        await ctx.send("[{}] feed track on [{}] channel.".format(feed_title, feed_channel.name))

    @feed.command(ignore_extra=False)
    async def list(self, ctx):
        await ctx.send('feedを削除します')

    @feed.command(ignore_extra=False)
    async def remove(self, ctx):
        await ctx.send('feedを削除します')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, BadArgument):
            return await ctx.send(error)
        if isinstance(error, MissingRequiredArgument):
            return await ctx.send(error)
        if isinstance(error, TooManyArguments):
            return await ctx.send(error)

def setup(bot):
    bot.add_cog(Feed(bot))
