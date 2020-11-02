# -*- coding: utf-8 -*-

import os
import time
import asyncio
import json
import difflib
import datetime
import traceback
import aiohttp
import aiofiles
import random
import discord
from discord.ext import commands
import crypto_bot
from math import *

TOKEN = os.environ.get("TRANSATLANTICBOT")
KEY = os.environ.get("PNWKEY")

command_dict = {
    "help": "Lists the commands and their descriptions",
    "help_commands": "ALIAS: help",
    "city": "Gets information about the specified city.\n\tUsage: URL and ID are both accepted.",
    "crypto": "🔐 MILITARY GRADE ENCRYPTION 🔐\n\tUsage: !crypto {ENC or DEC(encrypt or decrypt)} {TEXT TO CRYPT} {ID} {PASSWORD} {PSWD2 (optional)}"
}

morse = {'A': '.-', 'B': '-...',
         'C': '-.-.', 'D': '-..', 'E': '.',
         'F': '..-.', 'G': '--.', 'H': '....',
         'I': '..', 'J': '.---', 'K': '-.-',
         'L': '.-..', 'M': '--', 'N': '-.',
         'O': '---', 'P': '.--.', 'Q': '--.-',
         'R': '.-.', 'S': '...', 'T': '-',
         'U': '..-', 'V': '...-', 'W': '.--',
         'X': '-..-', 'Y': '-.--', 'Z': '--..',
         '1': '.----', '2': '..---', '3': '...--',
         '4': '....-', '5': '.....', '6': '-....',
         '7': '--...', '8': '---..', '9': '----.',
         '0': '-----', ', ': '--..--', '.': '.-.-.-',
         '?': '..--..', '/': '-..-.', '-': '-....-',
         '(': '-.--.', ')': '-.--.-'}

tab = "　" * 2


async def req(loc, key_provider=None):
    if key_provider is not None:
        url = f"https://politicsandwar.com/api/{loc}{key_provider}key={KEY}"
    elif "=" in loc:
        url = f"https://politicsandwar.com/api/{loc}&key={KEY}"
    else:
        url = f"https://politicsandwar.com/api/{loc}/?key={KEY}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.text()
            return json.loads(res)


def dict_to_string(d):
    newline = "\n"
    return f'```yml\n{newline.join((f"{key}: {value}" for key, value in d.items()))}\n```'


# update
async def update_war():
    start_time = time.time()
    print("\nWAR")
    print(f"Update Started - 0 secs")
    new = await req("wars?alliance_id=7536")
    print(f"Recieved Data - {time.time() - start_time} secs")
    if "success" in new.keys():
        lastcheck = datetime.datetime.utcnow() - datetime.timedelta(hours=0, minutes=6)
        wars = new["wars"]
        war_time = datetime.datetime.strptime(wars[0]["date"][:19], "%Y-%m-%dT%X")
        curr_war = 0
        while war_time >= lastcheck:
            current_war = wars[curr_war]
            war_time = datetime.datetime.strptime(wars[curr_war + 1]["date"][:19], "%Y-%m-%dT%X")
            if current_war["defenderAA"] == "None":
                curr_war += 1
                continue
            if current_war["attackerAA"] in ("Atlantian Council", "Atlantian Council Applicant"):
                defense_channel = await client.fetch_channel(717536088201363496)
            else:
                defense_channel = await client.fetch_channel(717815077624872971)

            spec_war = await req(f"war/{current_war['warID']}", "/&")
            current_war = spec_war["war"][0]

            attacker = await req(f"nation/id={spec_war['war'][0]['aggressor_id']}")
            defender = await req(f"nation/id={spec_war['war'][0]['defender_id']}")

            advantage = (
                ("soldiers", int(attacker["soldiers"]) - int(defender["soldiers"])),
                ("tanks", int(attacker["tanks"]) - int(defender["tanks"])),
                ("aircraft", int(attacker["aircraft"]) - int(defender["aircraft"])),
                ("ships", int(attacker["ships"]) - int(defender["ships"])),
                ("missiles", int(attacker["missiles"]) - int(defender["missiles"])),
                ("nukes", int(attacker["nukes"]) - int(defender["nukes"]))
            )

            a_adv = []
            d_adv = []
            n_adv = []

            for adv in advantage:
                if adv[1] > 0:
                    a_adv.append(adv[0])
                elif adv[1] < 0:
                    d_adv.append(adv[0])
                else:
                    n_adv.append(adv[0])

            advantage_txt = (
                ", ".join(a_adv),
                ", ".join(d_adv),
                ", ".join(n_adv)
            )

            adv_txt = ""

            if len(advantage_txt[0]):
                adv_txt += f"The attacker is strong in {advantage_txt[0]}, "
            else:
                adv_txt += "The attacker has no advantages, "

            if len(advantage_txt[1]):
                adv_txt += f"while the defender is strong in {advantage_txt[1]}. "
            else:
                adv_txt += "while the defender has no advantages. "

            if len(advantage_txt[2]):
                adv_txt += f"The two are equal in {advantage_txt[2]}"

            score_comp = f"\n🗒`  Category  |  Attacker  |  Defender  |` "
            compare = ("🎖score", "🏙cities", "🪖soldiers", "🚛tanks", "✈aircraft", "🚢ships", "🚀missiles", "☢nukes")

            for data in compare:
                score_comp += f"\n{data[0]}` {data[1:].ljust(10)} | {str(attacker[data[1:]]).rjust(10)} | {str(defender[data[1:]]).ljust(10)} |`"

            a_col = "diff" if int(current_war["aggressor_resistance"]) < 33 else "fix"
            d_col = "diff" if int(current_war["defender_resistance"]) < 33 else "fix"
            if int(current_war["aggressor_resistance"]) > 75:
                a_col = "yml"
            if int(current_war["defender_resistance"]) > 75:
                d_col = "yml"
            resist = f"**Attacker**```{a_col}\n---≡≡≡{''.join(['|' for _ in range(0, int(int(current_war['aggressor_resistance'])//2.5))]).center(40, ' ')}≡≡≡---\n```\n**Defender**```{d_col}\n---≡≡≡{''.join(['|' for _ in range(0, int(int(current_war['defender_resistance'])//2.5))]).center(40, ' ')}≡≡≡---\n```\n"

            links = f"\n⚔`War       `: https://politicsandwar.com/nation/war/timeline/war={current_war['war_id']}\n🗡`Attacker  `: https://politicsandwar.com/nation/id={attacker['nationid']}\n🛡`Defender  `: https://politicsandwar.com/nation/id={defender['nationid']}"

            info_text = f'**{tab}[{attacker["prename"]} __{attacker["name"]}__](https://politicsandwar.com/nation/id={attacker["nationid"]}) of [__{attacker["alliance"]}__](https://politicsandwar.com/alliance/id={attacker["allianceid"]}) has attacked [{defender["prename"]} __{defender["name"]}__](https://politicsandwar.com/nation/id={defender["nationid"]}) of [__{defender["alliance"]}__](https://politicsandwar.com/alliance/id={defender["allianceid"]}) for the reason, *{spec_war["war"][0]["war_reason"]}*\n{tab}{adv_txt}.**\n\n**__RESISTANCE__**\n{resist}\n\n**__RAW DATA__**\n{score_comp}\n\n**__LINKS__**\n{links}'

            emb = discord.Embed(
                title="⚔WAR REPORT⚔",
                description=info_text,
                color=discord.Color(0x00ff00)
            )
            emb.set_footer(
                icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
                text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by The Atlantian Council"
            )

            await defense_channel.send(embed=emb)
            curr_war += 1
        print(f"Update Success - {time.time() - start_time} secs")
    else:
        print(f"Upate Failure - {time.time() - start_time} secs")
    print(f"Waiting for next update - {time.time() - start_time} secs")


async def update_nations():
    start_time = time.time()
    print("\nNATION")
    print(f"Update Started - 0 secs")
    async with aiofiles.open("all_nations.json", mode="w") as nations:
        new = await req("nations")
        print(f"Recieved Data - {time.time() - start_time} secs")
        if "success" in new.keys():
            await nations.write(json.dumps(new))
            print(f"Update Success - {time.time() - start_time} secs")
        else:
            print(f"Upate Failure - {time.time() - start_time} secs")
    print(f"Waiting for next update - {time.time() - start_time} secs")


async def update():
    await client.wait_until_ready()
    while True:
        try:
            await update_war()
            await update_nations()
        except Exception:
            print("\n\nERROR HAPPENED\n")
            traceback.print_exc()

        await asyncio.sleep(5 * 60)


# run bot
client = commands.Bot(command_prefix=("^", "!", "also,\n", "also, ", "tst!"))
client.remove_command("help")

client.loop.create_task(update())


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="P&W")
    )
    print("---===≡≡≡BOT READY≡≡≡===---")


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.author == client.user:
        return

    sarcasm = ("looks sarcastically",
               "rolls eyes",
               "ignores",
               "scoffs")

    if 761905748585742366 in message.raw_mentions:
        if ("my" in message.content) and ("birthday" in message.content):
            await message.channel.send(f"Really? Happy Birthday, <@{message.author.id}>!")
            return
        if "good morning" in message.content:
            await message.channel.send(f"Thanks! Good morning, <@{message.author.id}>")
            return
        if "good night" in message.content:
            await message.channel.send(f"Thanks! Sweet dreams, <@{message.author.id}>")
            return
        if "stfu" in message.content:
            await message.channel.send("Uhhh... I would rather not.")
            end = 0
            for i in range(random.randint(2, 5)):
                await message.channel.send(f"```cs\n#{i + 1})\n```<@{message.author.id}>")
                end = i
            await asyncio.sleep(5)
            await message.author.send(f"```cs\n#{end + 2})\n```<@{message.author.id}>")
            return
        else:
            await message.channel.send("**HEY!** What did you ping me for?")
            await message.channel.send(f"<@{message.author.id}>")

    if random.random() < 0.03:
        await message.channel.send(f"*{random.choice(sarcasm)}*")

    if random.random() < 0.01220703125:
        await message.channel.send(":sparkles: You found a shiny Pokémon! :sparkles:")
        await asyncio.sleep(1)
        await message.channel.send(":skull_crossbones: It killed you and ran away. :skull_crossbones:")


@client.event
async def on_typing(channel, user, _):
    if random.random() < 0.05:
        await channel.send(
            f"Hey, come look at this fool, <@{user.id}>, who is typing a very **LONG** message! What a stuck-up asshole! What does he/she do better than any of us that makes him/her write a long message?")

    return


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
            emb.set_footer(
                icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
                text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
            )

            await ctx.send(embed=emb)
            return

    theCity = await req(f"city/id={c_id}")
    if "error" in theCity.keys():
        theCity["name"], theCity["cityid"] = "CITY NOT FOUND", c_id
    emb = discord.Embed(
        title=f"{theCity['name']} - [{theCity['cityid']}]",
        description=dict_to_string(theCity),
        color=discord.Color(0x00ff00)
    )
    emb.set_footer(
        icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
        text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
    )

    await ctx.send(embed=emb)
    return


@client.command()
async def crypto(ctx, enc, text, iv, password, salt="Yenigma-2"):
    random.seed(iv)
    iv = random.getrandbits(256)
    random.seed()
    crypt = crypto_bot.Crypt(password, salt, iv)
    if enc == "ENC":
        txt = crypt.encrypt(text)
    elif enc == "DEC":
        txt = crypt.decrypt(text)
    else:
        txt = "You got something wrong: try ENC or DEC"

    emb = discord.Embed(
        title="Encryption" if enc == "ENC" else "Decryption",
        description=f"```\n{txt}\n```",
        color=discord.Color(0x00ff00)
    )
    emb.set_footer(
        icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
        text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
    )

    await ctx.send(embed=emb)
    return


@client.command()
async def calc(ctx, *args):
    await ctx.send(eval(" ".join(args), {}, {}))


@client.command()
async def war(ctx, w_id):
    if w_id.startswith("http"):
        w_id = w_id[w_id.find("=") + 1:].rstrip("/")
    else:
        w_id = int(w_id)

    spec_war = await req(f"war/{w_id}", "/&")
    current_war = spec_war["war"][0]

    attacker = await req(f"nation/id={spec_war['war'][0]['aggressor_id']}")
    defender = await req(f"nation/id={spec_war['war'][0]['defender_id']}")

    advantage = (
        ("soldiers", int(attacker["soldiers"]) - int(defender["soldiers"])),
        ("tanks", int(attacker["tanks"]) - int(defender["tanks"])),
        ("aircraft", int(attacker["aircraft"]) - int(defender["aircraft"])),
        ("ships", int(attacker["ships"]) - int(defender["ships"])),
        ("missiles", int(attacker["missiles"]) - int(defender["missiles"])),
        ("nukes", int(attacker["nukes"]) - int(defender["nukes"]))
    )

    a_adv = []
    d_adv = []
    n_adv = []

    for adv in advantage:
        if adv[1] > 0:
            a_adv.append(adv[0])
        elif adv[1] < 0:
            d_adv.append(adv[0])
        else:
            n_adv.append(adv[0])

    advantage_txt = (
        ", ".join(a_adv),
        ", ".join(d_adv),
        ", ".join(n_adv)
    )

    adv_txt = ""

    if len(advantage_txt[0]):
        adv_txt += f"The attacker is strong in {advantage_txt[0]}, "
    else:
        adv_txt += "The attacker has no advantages, "

    if len(advantage_txt[1]):
        adv_txt += f"while the defender is strong in {advantage_txt[1]}. "
    else:
        adv_txt += "while the defender has no advantages. "

    if len(advantage_txt[2]):
        adv_txt += f"The two are equal in {advantage_txt[2]}"

    score_comp = f"\n🗒`  Category  |  Attacker  |  Defender  |` "
    compare = ("🎖score", "🏙cities", "🪖soldiers", "🚛tanks", "✈aircraft", "🚢ships", "🚀missiles", "☢nukes")

    for data in compare:
        score_comp += f"\n{data[0]}` {data[1:].ljust(10)} | {str(attacker[data[1:]]).rjust(10)} | {str(defender[data[1:]]).ljust(10)} |`"
    
    a_col = "diff" if int(current_war["aggressor_resistance"]) < 33 else "fix"
    d_col = "diff" if int(current_war["defender_resistance"]) < 33 else "fix"
    if int(current_war["aggressor_resistance"]) > 75:
        a_col = "yml"
    if int(current_war["defender_resistance"]) > 75:
        d_col = "yml"
    resist = f"**Attacker**```{a_col}\n---≡≡≡{''.join(['|' for _ in range(0, int(int(current_war['aggressor_resistance'])//2.5))]).center(40, ' ')}≡≡≡---\n```\n**Defender**```{d_col}\n---≡≡≡{''.join(['|' for _ in range(0, int(int(current_war['defender_resistance'])//2.5))]).center(40, ' ')}≡≡≡---\n```\n"

    links = f"\n⚔`War       `: https://politicsandwar.com/nation/war/timeline/war={current_war['war_id']}\n🗡`Attacker  `: https://politicsandwar.com/nation/id={attacker['nationid']}\n🛡`Defender  `: https://politicsandwar.com/nation/id={defender['nationid']}"

    info_text = f'**{tab}[{attacker["prename"]} __{attacker["name"]}__](https://politicsandwar.com/nation/id={attacker["nationid"]}) of [__{attacker["alliance"]}__](https://politicsandwar.com/alliance/id={attacker["allianceid"]}) has attacked [{defender["prename"]} __{defender["name"]}__](https://politicsandwar.com/nation/id={defender["nationid"]}) of [__{defender["alliance"]}__](https://politicsandwar.com/alliance/id={defender["allianceid"]}) for the reason, *{spec_war["war"][0]["war_reason"]}*\n{tab}{adv_txt}.**\n\n**__RESISTANCE__**\n{resist}\n\n**__RAW DATA__**\n{score_comp}\n\n**__LINKS__**\n{links}'

    emb = discord.Embed(
        title="⚔WAR REPORT⚔",
        description=info_text,
        color=discord.Color(0x00ff00)
    )
    emb.set_footer(
        icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
        text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by The Atlantian Council"
    )

    await ctx.send(embed=emb)


@client.command(name="depo")
async def depo(ctx, *args):
    await ctx.send("`!depo`? More like `!debt`")


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
        emb.set_footer(
            icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
            text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
        )

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
                    icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
                    text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
                )

                await ctx.send(embed=emb)
                return
        else:
            txt = f"```yml\n{f'{spec_command}: {command_dict[spec_command]}'}\n```"
        emb = discord.Embed(
            title=f"Help - {spec_command}",
            description=txt,
            color=discord.Color(0x00ff00)
        )
        emb.set_footer(
            icon_url="https://i.ibb.co/QXJrhmC/Atlantic-Council.png",
            text=f"P&W bot for ANYONE, unlike SOME OTHER BOT  -  Requested by {ctx.author.name}"
        )

        await ctx.send(embed=emb)
        return


client.run(TOKEN)
