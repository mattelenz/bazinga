import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

class Catdog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # load in our api keys
        self.cat_api_key = os.getenv('CAT_API_KEY')
        self.dog_api_key = os.getenv('DOG_API_KEY')

    @app_commands.command(name="dog", description="Get a random dog picture!")
    async def dog(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # adding the dog api key to the header
        headers = {
            'x-api-key': self.dog_api_key
        }
        async with aiohttp.ClientSession() as session:
            try:
                # gets a dog picture url
                async with session.get('https://api.thedogapi.com/v1/images/search', headers=headers) as response:
                    # error checking
                    if response.status != 200:
                        await interaction.followup.send("Sorry, I couldn't fetch a dog pic right now. Please try again later.")
                        return
                    # put the received json in a variable
                    data = await response.json()
                    if not data:
                        await interaction.followup.send("Sorry, I couldn't find a dog picture.")
                        return
                    # get the url from the received json
                    dog_image_url = data[0]['url']
                    # send dog
                    await interaction.followup.send(dog_image_url)
            # error checking
            except aiohttp.ClientError as e:
                print(f"Error fetching dog image: {e}")
                await interaction.followup.send("Sorry, I couldn't fetch a dog pic right now. Please try again later.")

    # the cat command works essentially the same way as the dog command
    @app_commands.command(name="cat", description="Get a random cat picture!")
    async def cat(self, interaction: discord.Interaction):
        await interaction.response.defer()

        headers = {
            'x-api-key': self.cat_api_key
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get('https://api.thecatapi.com/v1/images/search', headers=headers) as response:
                    if response.status != 200:
                        await interaction.followup.send("Sorry, I couldn't fetch a cat pic right now. Please try again later.")
                        return
                    
                    data = await response.json()
                    if not data:
                        await interaction.followup.send("Sorry, I couldn't find a cat picture.")
                        return
                    
                    cat_image_url = data[0]['url']
                    await interaction.followup.send(cat_image_url)
            except aiohttp.ClientError as e:
                print(f"Error fetching cat image: {e}")
                await interaction.followup.send("Sorry, I couldn't fetch a cat pic right now. Please try again later.")

async def setup(bot):
    await bot.add_cog(Catdog(bot))
