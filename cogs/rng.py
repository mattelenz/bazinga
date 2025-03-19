import random
import discord
from discord import app_commands
from discord.ext import commands

class rng(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    # simple coinflipper using the random library
    @app_commands.command(name="flip", description="Flip a coin.")
    async def flip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"The coin landed on: {result}")

    # slash command for betting on a coinflip
    @app_commands.command(name="betflip", description="Flip a coin and betsome $GBP")
    @app_commands.describe(
        choice="Choose 'heads' or 'tails'.",
        bet="Amount of coins to bet."
        )
    async def betflip(self, interaction: discord.Interaction, choice: str, bet: int):
        choice = choice.lower()
        valid_choices = ["heads", "tails"]
        # check user input
        if choice not in valid_choices:
            await interaction.response.send_message("Invalid choice. Please choose 'heads' or 'tails'.", ephemeral=True)
            return
        
        db_cog = self.bot.get_cog("DatabaseCog")
        user_currency = db_cog.get_currency(interaction.user.id)
        # make sure user has enough currency
        if user_currency < bet:
            await interaction.response.send_message(f"You don't have enough $GBP to bet that much. You have {user_currency} $GBP.", ephemeral=True)
            return
        
        # bot choice
        result = random.choice(["heads", "tails"])

        # compare user choice to bot choice
        if result == choice:
            db_cog.update_currency(interaction.user.id, bet)
            await interaction.response.send_message(f"Your choice: {choice}. The coin landed on: {result.capitalize()}. You won {bet} $GBP!", ephemeral=True)
            return
        else:
            db_cog.update_currency(interaction.user.id, -bet)
            await interaction.response.send_message(f"Your choice: {choice}. The coin landed on: {result.capitalize()}. You lost {bet} $GBP.", ephemeral=True)
            return
        
    # slash command to roll an x sided die, really just picking a number within a range
    @app_commands.command(name="diceroll", description="Roll a dice with a specified number of sides.")
    @app_commands.describe(choice="Choose how many sides the die should have.")
    async def diceroll(self, interaction: discord.Interaction, choice: int):
        # make sure the die has sides
        if choice <= 1:
            await interaction.response.send_message("Please choose a positive number greater than 1.", ephemeral=True)
            return
        
        # pick a number
        random_number = random.randint(1, choice)
        await interaction.response.send_message(f"I rolled {random_number} on a d{choice}.")
        return


async def setup(bot):
    await bot.add_cog(rng(bot))