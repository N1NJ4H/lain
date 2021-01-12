import discord
from discord.ext import commands
from discord.ext import tasks

import datetime
import pytz

class WorldTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(ignore_extra=False)
    async def time(self, ctx):
        print("in time1")
        tokyo = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        amsterdam = datetime.datetime.now(pytz.timezone('Europe/Amsterdam'))
        print("in time2")
        await ctx.send('Tokyo: {}'.format(tokyo))
        await ctx.send('Amsterdam: {}'.format(amsterdam))

def setup(bot):
    bot.add_cog(WorldTime(bot))