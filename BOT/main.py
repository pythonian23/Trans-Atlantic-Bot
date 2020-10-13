import os
import requests
import discord
from discord.ext import commands


TOKEN = os.environ.get("TRANSATLANTICBOT")
KEY = os.environ.get("PNWKEY")


def req(loc):
    if "=" in loc:
        return requests.get(f"https://politicsandwar.com/api/{loc}&key={KEY}").json()
    else:
        return requests.get(f"https://politicsandwar.com/api/{loc}?key={KEY}").json()


# run bot
client = commands.Bot(command_prefix=("^", "!"))


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="P&W")
    )
    print("BOT READY")


@client.command()
async def city(ctx, *args):
    c_id = " ".join(args).strip(" ")
    if not c_id.isdigit():
        if c_id.startswith("http"):
            c_id = c_id[c_id.find("=") + 1:].rstrip("/")
        else:
            emb = discord.Embed(
                title="City - Error",
                description=f"Your format was wrong, and I couldn't understand it. Try a link or an ID",
                color=discord.Color(0x00ff00)
            )
            emb.set_footer(text=f"P&W bot for ANYONE, unlike @Locutus#7602     -     Requested by {ctx.author.name}")
            await ctx.channel.send(embed=emb)
            return

    theCity = req(f"city/id={c_id}")
    if "error" in theCity.keys():
        theCity["name"], theCity["cityid"] = "CITY NOT FOUND", c_id
    emb = discord.Embed(
        title=f"{theCity['name']} - [{theCity['cityid']}]",
        description=f"```py\n{theCity}\n```",
        color=discord.Color(0x00ff00)
    )
    emb.set_footer(text=f"P&W bot for ANYONE, unlike @Locutus#7602     -     Requested by {ctx.author.name}")

    await ctx.channel.send(embed=emb)
    return

client.run(TOKEN)
