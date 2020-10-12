import os
import discord
from discord.ext import commands


TOKEN = os.environ.get("TRANSATLANTICBOT")


client = commands.Bot(command_prefix=("^", "!"))


@client.event
async def on_ready():
    print("BOT READY")


@client.command()
async def Embed(ctx):
    emb = discord.Embed(title="Embed", description="")
    emb.set_footer(text="FOOTER")
    await ctx.channel.send(embed=emb)


client.run(TOKEN)
