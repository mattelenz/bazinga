import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

class Cat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cat_api_key = os.getenv('CAT_API_KEY')

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
    await bot.add_cog(Cat(bot))
