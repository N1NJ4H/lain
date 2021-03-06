import discord
from discord.ext import commands
from discord.ext import tasks

# feed関連のモジュール
import feedparser

#from prettytable import from_db_cursor

import re

sql_create_feed_info_tbl = '''
CREATE TABLE IF NOT EXISTS feed_info (
	feed_url text PRIMARY KEY,
	feed_title text,
    channel_id text
)
'''
sql_create_feed_entry_tbl = '''
CREATE TABLE IF NOT EXISTS feed_entry (
	entry_url text PRIMARY KEY,
    feed_url text,
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
            await ctx.send('This command need sub commands.')
    
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
        # URLがFEEDとして正しく解析できるかをテスト
        try:
            feed_title = feeds.feed.title
        except:
            await ctx.send('Failed URL analyze. Is this correct feed url?')
            return False
        # feed_infoテーブルに同じURLが追加されている場合は、中止する
        cur = self.bot.sqlite3.cursor()
        sql = 'select * from feed_info where feed_url = ?'
        cur.execute(sql, (url, ))
        record = cur.fetchall()
        if len(record) > 0:
            await ctx.send('This URL is already registered')
            return False
        # FEEDカテゴリに追加する
        feed_category_id = self.bot.category_name2category_id(ctx.guild, 'FEED')
        feed_category = ctx.guild.get_channel(feed_category_id)
        # 指定されたチャンネルを作成し、チャンネルIDを返す
        feed_channel_id = await self.ensure_feed_channel(feed_category, channel)
        feed_channel = ctx.guild.get_channel(feed_channel_id)
        # feed_infoテーブルにレコードを追加する
        sql = 'insert into feed_info (feed_url, feed_title, channel_id) values (?, ?, ?)'
        cur.execute(sql, (url, feed_title, feed_channel_id))
        self.bot.sqlite3.commit()
        # 正常に登録できたメッセージを送信する
        await ctx.send("[{}] feed track on [{}] channel.".format(feed_title, feed_channel.name))

    @feed.command(ignore_extra=False)
    async def list(self, ctx):
        cur = self.bot.sqlite3.cursor()
        cur.execute('select FEED_TITLE, FEED_URL, CHANNEL_ID from feed_info')
        records = cur.fetchall()
        for row in records:
            channel = ctx.guild.get_channel(int(row[2]))
            await ctx.send("{} {} {}".format(row[0], channel.name, row[1]))

    @feed.command(ignore_extra=False)
    async def remove(self, ctx, url):
        cur = self.bot.sqlite3.cursor()
        cur.execute('select channel_id from feed_info where feed_url = ?', (url, ))
        record = cur.fetchall()
        if not record:
            # feed_infoテーブルに該当のURLが存在しない。
            await ctx.send('This URL is not registered')
            return False
        else:
            # feed_infoテーブルに該当のURLが存在する。
            channel_id = int(record[0][0])
            channel = ctx.guild.get_channel(channel_id)
            # 他にこのチャンネルを使っているfeedが存在するかを確認する
            cur.execute('select * from feed_info where channel_id = ?', (channel_id, ))
            records = cur.fetchall()
            if len(records) > 1:
                # 他にもチャンネルを使用しているfeedが存在する
                pass
            else:
                # 該当チャンネルを使用しているfeedは1つだけなのでチャンネルも削除する
                await channel.delete()
                cur.execute('delete from feed_info where feed_url = ?', (url,))
                self.bot.sqlite3.commit()
            # 該当のFEED URLのエントリは全て削除する
            cur.execute('delete from feed_entry where feed_url = ?', (url,))
            self.bot.sqlite3.commit()
            await ctx.send("This URL's feed remove")

    @tasks.loop(minutes=10)
    async def feed_fetch(self):
        p = re.compile(r"<[^>]*?>") # HTMLタグ削除用正規表現
        cur = self.bot.sqlite3.cursor()
        cur.execute('select feed_url, channel_id from feed_info')
        feeds = cur.fetchall()
        for feed in feeds:
            (feed_url, channel_id) = (feed[0], feed[1])
            channel = self.bot.get_channel(int(channel_id))
            d = feedparser.parse(feed_url)
            for entry in d.entries:
                # すでに閲覧したエントリ情報ではないことを確認
                cur.execute('select * from feed_entry where entry_url = ?', (entry.link, ))
                e = cur.fetchall()
                if len(e) > 0:
                    # すでに閲覧済みエントリなのでskipする
                    continue
                else:
                    try:
                        # 初めてのエントリなのでデータベースに保存して、
                        sql = 'insert into feed_entry (entry_url, feed_url) values (?, ?)'
                        cur.execute(sql, (entry.link, feed_url))
                        self.bot.sqlite3.commit()
                        # discordにエントリ情報を送信
                        summary = p.sub("", entry.summary)
                        await channel.send("[TITLE] {}".format(entry.title))
                        await channel.send("[URL] {}".format(entry.link))
                        await channel.send("```\n{}\n```".format(summary[0:1000]))
                    except:
                        continue
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.feed_fetch.start()

def setup(bot):
    bot.add_cog(Feed(bot))
