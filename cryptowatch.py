import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from urllib.request import urlopen as uReq, Request
from bs4 import BeautifulSoup as soup
import sqlite3
import os
from dotenv import load_dotenv
import requests, json
import math

# ------------------------------------------------
# CONFIGS
# ------------------------------------------------

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
defaultChannel = int(os.getenv("DEFAULT_CHANNEL")) # current-interest

ACTIVITY_STATUS = os.getenv("ACTIVITY_STATUS")
ACTIVITY_TYPE = os.getenv("ACTIVITY_TYPE")
ACTIVITY_TEXT = os.getenv("ACTIVITY_TEXT")

print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "[1/3] Assigning SCV for launch...")
print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "Loaded configs:")
print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "Activity status: " + ACTIVITY_STATUS)
print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "Activity type: " + ACTIVITY_TYPE)
print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "Activity text: " + ACTIVITY_TEXT)
print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "Channel: " + str(defaultChannel))

# ------------------------------------------------
# INITIALIZATION
# ------------------------------------------------

clientStatus = ""
if ACTIVITY_STATUS == "online":
	clientStatus = discord.Status.online
elif ACTIVITY_STATUS == "offline":
	clientStatus = discord.Status.offline
elif ACTIVITY_STATUS == "idle":
	clientStatus = discord.Status.idle
elif ACTIVITY_STATUS == "busy":
	clientStatus = discord.Status.dnd
else:
	clientStatus = discord.Status.online

clientActivityType = ""
if ACTIVITY_TYPE == "playing":
	clientActivityType = discord.ActivityType.playing
elif ACTIVITY_TYPE == "streaming":
	clientActivityType = discord.ActivityType.streaming
elif ACTIVITY_TYPE == "listening":
	clientActivityType = discord.ActivityType.listening
elif ACTIVITY_TYPE == "watching":
	clientActivityType = discord.ActivityType.watching
elif ACTIVITY_TYPE == "custom":
	clientActivityType = discord.ActivityType.custom
elif ACTIVITY_TYPE == "competing":
	clientActivityType = discord.ActivityType.competing
else:
	clientActivityType = discord.ActivityType.playing

if ACTIVITY_TEXT is not None:
	clientActivityText = ACTIVITY_TEXT
else:
	clientActivityText = ""

intents = discord.Intents().all()
client = commands.Bot(command_prefix = "$", activity=discord.Activity(type=clientActivityType, name=clientActivityText), status=clientStatus, intents=intents)

print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "[2/3] Initializing connection to Korhal network.")

waitTime = 305 # 5 minutes 5 seconds (rate limit is 2 requests per 10 minutes)
counter = 0
gasCounter = 0
gasWaitTime = 15
channels = [986240291445047376, 986243878195724328]

# ------------------------------------------------
# EVENTS SECTION
# ------------------------------------------------

@client.event
async def on_ready():
	print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "[3/3] Battlecruiser operational.")

async def check_gas():
	global gasCounter
	global defaultChannel
	while not client.is_closed():
		gasCounter += 1

		timestamp = datetime.now()
		time = timestamp.strftime(r"%I:%M %p")

		content = requests.get("https://www.nftsensei.xyz/api/gas")
		gas = json.loads(content.content)
		price = int(gas["blockPrices"][0]["estimatedPrices"][2]["price"])
		confidence = float(gas["blockPrices"][0]["estimatedPrices"][2]["confidence"])
		maxFee = float(gas["blockPrices"][0]["estimatedPrices"][2]["maxFeePerGas"])
		maxPriorityFee = float(gas["blockPrices"][0]["estimatedPrices"][2]["maxPriorityFeePerGas"])
		baseFee = float(gas["blockPrices"][0]["baseFeePerGas"])
		blockNumber = int(gas["blockPrices"][0]["blockNumber"])
		currentBlockNumber = int(gas["currentBlockNumber"])

		print("[" + datetime.now().strftime(r"%I:%M:%S %p") + "] " + "[" + str(gasCounter) + "] Reading estimated median gas price on " + str(price) + " gwei with a confidence of " + str(confidence) + "%")

		if price <= 30:
			await client.wait_until_ready()
			embed = discord.Embed(title="<a:alarmred:986241450322833468> Gas price has reached " + str(price) + " gwei", color=0xf0acb4)
			embed.add_field(name="Confidence", value=str(confidence) + "%", inline=False)
			embed.add_field(name="Max Fee", value=str(maxFee), inline=False)
			embed.add_field(name="Max Priority Fee", value=str(maxPriorityFee), inline=False)
			embed.add_field(name="Base Fee", value=str(baseFee), inline=False)
			embed.add_field(name="Block Number", value=str(blockNumber), inline=False)
			# embed.add_field(name="Current Block Number", value=str(currentBlockNumber), inline=False)
			for channel in channels:
				notifChannel = client.get_channel(channel)
				await notifChannel.send(embed=embed)
				# await notifChannel.send("<a:alarmred:986241450322833468> Gas price has reached a median estimate of " + str(price) + " gwei with a confidence of " + str(confidence) + "% <a:alarmred:986241450322833468>")
			gasWaitTime = 120
		else:
			gasWaitTime = 8

		# await cryptoChannel.edit(topic=result)

		await asyncio.sleep(gasWaitTime) # task loop wait time

client.loop.create_task(check_gas())	
client.run(TOKEN)