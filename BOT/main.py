import os
import difflib
import requests
import discord
from discord.ext import commands

TOKEN = os.environ.get("TRANSATLANTICBOT")
KEY = os.environ.get("PNWKEY")

command_dict = {
    "help": "Lists the commands and their descriptions",
    "help_commands": "ALIAS: help",
    "city": "Gets information about the specified city. URL and ID are both accepted.",
}


def req(loc):
    if "=" in loc:
        return requests.get(f"https://politicsandwar.com/api/{loc}&key={KEY}").json()
    else:
        return requests.get(f"https://politicsandwar.com/api/{loc}?key={KEY}").json()


# run bot
client = commands.Bot(command_prefix=("^", "!", "also,\n", "also, "))
client.remove_command("help")


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
            await ctx.send(embed=emb)
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

    await ctx.send(embed=emb)
    return


@client.command(name="help", aliases=["help_commands"])
async def help_commands(ctx, spec_command=None):
    if spec_command is None:
        txts = []
        for key, val in command_dict.items():
            txts.append(f"{key}: {val}")

        joined = "\n".join(txts)
        emb = discord.Embed(
            title="Help",
            description=f"```yml\n{joined}\n```",
            color=discord.Color(0x00ff00)
        )
        emb.set_footer(text=f"P&W bot for ANYONE, unlike @Locutus#7602     -     Requested by {ctx.author.name}")

        await ctx.send(embed=emb)
        return
    else:
        if spec_command not in command_dict.keys():
            try:
                spec_command = difflib.get_close_matches(spec_command, command_dict.keys())[0]
                txt = f"```yml\n{f'{spec_command}: {command_dict[spec_command]}'}\n\nCommand not found, but is this what you're looking for?\n```"
            except IndexError:
                emb = discord.Embed(
                    title=f"Help - {spec_command}",
                    description="```yml\nCommand does not exist.\n```",
                    color=discord.Color(0x00ff00)
                )
                emb.set_footer(
                    text=f"P&W bot for ANYONE, unlike @Locutus#7602     -     Requested by {ctx.author.name}")

                await ctx.send(embed=emb)
                return
        else:
            txt = f"```yml\n{f'{spec_command}: {command_dict[spec_command]}'}\n```"
        emb = discord.Embed(
            title=f"Help - {spec_command}",
            description=txt,
            color=discord.Color(0x00ff00)
        )
        emb.set_footer(text=f"P&W bot for ANYONE, unlike @Locutus#7602     -     Requested by {ctx.author.name}")

        await ctx.send(embed=emb)
        return


client.run(TOKEN)
