import os
from datetime import datetime
import discord
from discord import app_commands, Intents, Client, Interaction
from discord.ext import tasks
from dotenv import load_dotenv
import requests
import webscraper

# load discord token from .env
load_dotenv()
DISCORD_TOKEN = os.getenv('TOKEN')
CHANNEL_ID = 1028835361868218442

# get the current time and date
def timedate():
    now = datetime.now()
    dt = now.strftime('%m/%d/%Y %H:%M:%S')
    return dt

# request api for discord bot
while True:
    data = requests.get('https://discord.com/api/v10/users/@me', 
    headers={
        'Authorization': f'Bot {DISCORD_TOKEN}'
    }).json

    # if the token is correct, continue code
    if data.__get__('id', None):
        break

# create class to sync global tree command, start check news article task, and send message when ready
class CyberBot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self) -> None:
        await self.tree.sync()
        self.check_new.start()

    async def on_ready(self):
        print(f'Currently logged in as {self.user} at {timedate()}. (ID: {self.user.id})')

    @tasks.loop(minutes=30)
    async def check_new(self):
        channel = self.get_channel(CHANNEL_ID)
        print(f'{self.user} compared the latest cybersecurity news articles.')
        if webscraper.compareTitle():
            print('No new articles.')
        else:
            webscraper.writeTitle() # scrapes the latest article title for comparison
            embed=discord.Embed(title=webscraper.scrapeTitle(0), url=webscraper.scrapeLink(0), color=discord.Color.purple())
            embed.set_thumbnail(url=webscraper.scrapeImage(0))
            embed.add_field(name="Description:", value=webscraper.scrapeDate(0)+'\n'+webscraper.scrapeDesc(0), inline=False)
            await channel.send(embed=embed)
            print(f'New article sent in {channel}.')

    @check_new.before_loop
    async def before_start(self):
        await self.wait_until_ready()

# create client instance and set intent
client = CyberBot(intents=Intents.default())

# create a tree command to display cybersecurity articles when requested
@client.tree.command(name='cybernews', description='display cybersecurity related articles')
async def cyber_news(interaction: Interaction):
    print(f'{interaction.user} used the cybernews command at {timedate()}.')
    embed=discord.Embed(title=webscraper.scrapeTitle(0), url=webscraper.scrapeLink(0), color=discord.Color.purple())
    embed.set_thumbnail(url=webscraper.scrapeImage(0))
    embed.add_field(name="Description:", value=webscraper.scrapeDate(0)+'\n'+webscraper.scrapeDesc(0), inline=False)
    await interaction.response.send_message(embed=embed)

# start the bot process
if __name__ == '__main__':
    client.run(DISCORD_TOKEN)