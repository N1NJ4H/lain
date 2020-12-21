from discord.ext import commands
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
    timestamp timestamp
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
            await ctx.send('このコマンドにはサブコマンドが必要です。')

    @feed.command()
    async def add(self, ctx):
        await ctx.send('feedを追加します')

    # roleコマンドのサブコマンド
    # 指定したユーザーから指定した役職を剥奪する。
    @feed.command()
    async def remove(self, ctx):
        await ctx.send('feedを削除します')

def setup(bot):
    bot.add_cog(Feed(bot))