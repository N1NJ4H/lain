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
        tokyo = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        newyork = datetime.datetime.now(pytz.timezone('America/New_York'))
        amsterdam = datetime.datetime.now(pytz.timezone('Europe/Amsterdam'))

        await ctx.send("[Tokyo] {}".format(tokyo))
        await ctx.send("[NewYork] {}".format(newyork))
        await ctx.send("[Amsterdam] {}".format(amsterdam))

def setup(bot):
    bot.add_cog(WorldTime(bot))
