import os
import time
import json
import difflib
import datetime
import asyncio
import threading
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


def req(loc, key_provider=None):
    if key_provider is not None:
        return requests.get(f"https://politicsandwar.com/api/{loc}{key_provider}key={KEY}").json()
    if "=" in loc:
        return requests.get(f"https://politicsandwar.com/api/{loc}&key={KEY}").json()
    else:
        return requests.get(f"https://politicsandwar.com/api/{loc}/?key={KEY}").json()


def dict_to_string(d):
    newline = "\n"
    return f'```yml\n{newline.join((f"{key}: {value}" for key, value in d.items()))}\n```'


async def get_nation(ctx, n_id):
    if not n_id.isdigit():
        if n_id.startswith("http"):
            n_id = n_id[n_id.find("=") + 1].rstrip("/")
        else:
            pass
    return n_id


# update
async def update_war():
    start_time = time.time()
    print("\nWAR")
    print(f"Update Started - 0 secs")
    new = req("wars?alliance_id=7536")
    print(f"Recieved Data - {time.time() - start_time} secs")
    if "success" in new.keys():
        lastcheck = datetime.datetime.utcnow() - datetime.timedelta(minutes=21)
        wars = new["wars"]
        war_time = datetime.datetime.strptime(wars[0]["date"][:19], "%Y-%m-%dT%X")
        war = 0
        while war_time >= lastcheck:
            current_war = wars[war]
            war_time = datetime.datetime.strptime(wars[war + 1]["date"][:19], "%Y-%m-%dT%X")
            if current_war["attackerAA"] in ("Atlantian Council", "Atlantian Council Applicant"):
                defense_channel = await client.fetch_channel(717536088201363496)
            else:
                defense_channel = await client.fetch_channel(717815077624872971)

            spec_war = req(f"war/{current_war['warID']}", "/&")

            emb = discord.Embed(
                title="WAR REPORT",
                description=dict_to_string(spec_war),
                color=discord.Color(0x00ff00)
            )
            emb.set_footer(text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by The Atlantian Council")

            await defense_channel.send(embed=emb)
            war += 1
        print(f"Update Success - {time.time() - start_time} secs")
    else:
        print(f"Upate Failure - {time.time() - start_time} secs")
    print(f"Waiting for next update - {time.time() - start_time} secs")


async def update_nations():
    start_time = time.time()
    print("\nNATION")
    print(f"Update Started - 0 secs")
    with open("all_nations.json", "w") as nations:
        new = req("nations")
        print(f"Recieved Data - {time.time() - start_time} secs")
        if "success" in new.keys():
            json.dump(new, nations)
            print(f"Update Success - {time.time() - start_time} secs")
        else:
            print(f"Upate Failure - {time.time() - start_time} secs")
    print(f"Waiting for next update - {time.time() - start_time} secs")


def update():
    while True:
        asyncio.run(update_war())
        asyncio.run(update_nations())

        time.sleep(60 * 20)


updater = threading.Thread(target=update, daemon=True)


# run bot
client = commands.Bot(command_prefix=("^", "!", "also,\n", "also, ", "tst!"))
client.remove_command("help")


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="P&W")
    )
    print("BOT READY")

    updater.start()


@client.command()
async def city(ctx, *c_id):
    c_id = " ".join(c_id)
    if not c_id.isdigit():
        if c_id.startswith("http"):
            c_id = c_id[c_id.find("=") + 1:].rstrip("/")
        else:
            emb = discord.Embed(
                title="City - Error",
                description=f"Your format was wrong, and I couldn't understand it. Try a link or an ID",
                color=discord.Color(0x00ff00)
            )
            emb.set_footer(text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}")

            await ctx.send(embed=emb)
            return

    theCity = req(f"city/id={c_id}")
    if "error" in theCity.keys():
        theCity["name"], theCity["cityid"] = "CITY NOT FOUND", c_id
    emb = discord.Embed(
        title=f"{theCity['name']} - [{theCity['cityid']}]",
        description=dict_to_string(theCity),
        color=discord.Color(0x00ff00)
    )
    emb.set_footer(text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}")

    await ctx.send(embed=emb)
    return


@client.command()
async def military(ctx, n_id):
    pass


@client.command()
async def depo(ctx, *args):
    ctx.send("`!depo`? More like `!debt`")


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
        emb.set_footer(text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}")

        await ctx.send(embed=emb)
        return
    else:
        if spec_command not in command_dict.keys():
            try:
                spec_command = difflib.get_close_matches(spec_command, command_dict.keys())[0]
                txt = f"```yml\n{f'{spec_command}: {command_dict[spec_command]}'}\
\n\nCommand not found, but is this what you're looking for?\n```"
            except IndexError:
                emb = discord.Embed(
                    title=f"Help - {spec_command}",
                    description="```yml\nCommand does not exist.\n```",
                    color=discord.Color(0x00ff00)
                )
                emb.set_footer(
                    text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}")

                await ctx.send(embed=emb)
                return
        else:
            txt = f"```yml\n{f'{spec_command}: {command_dict[spec_command]}'}\n```"
        emb = discord.Embed(
            title=f"Help - {spec_command}",
            description=txt,
            color=discord.Color(0x00ff00)
        )
        emb.set_footer(text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}")

        await ctx.send(embed=emb)
        return


client.run(TOKEN)
