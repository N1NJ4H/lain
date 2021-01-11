import discord
from discord.ext import commands
from discord.ext import tasks

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter

class CurrencyConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(ignore_extra=False)
    async def cc(self, ctx, c_from, c_to, value):
        c = CurrencyRates()
        b = BtcConverter()
        c_from_upper = c_from.upper()
        c_to_upper = c_to.upper()
        if "BTC" in [c_from_upper, c_to_upper]:
            # BTC 変換
            if c_from_upper == 'BTC':
                cc = b.convert_btc_to_cur(float(value), c_to_upper)
                await ctx.send('[{}] -> [{}] = {} -> {}'.format(c_from_upper, c_to_upper, float(value), cc))
            if c_to_upper== 'BTC':
                cc = b.convert_to_btc(float(value), c_from_upper)
                await ctx.send('[{}] -> [{}] = {} -> {}'.format(c_from_upper, c_to_upper, float(value), cc))
        else:
            cc = c.convert(c_from_upper, c_to_upper, float(value))
            await ctx.send('[{}] -> [{}] = {} -> {}'.format(c_from_upper, c_to_upper, float(value), cc))
 
def setup(bot):
    bot.add_cog(CurrencyConverter(bot))