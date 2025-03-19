import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # help slash command to make users aware of what the bot can do
    @app_commands.command(name="help", description="Get a list of commands to use with the bot.")
    async def help_me(self, interaction: discord.Interaction):
        # list to add all the commands to
        commands_list = [
            "/award - award a chosen user with $GBP\n"
            "/balance - check how many $GBP you have\n"
            "/betflip - bet on a coinflip\n"
            "/blackjack - play a hand of blackjack\n"
            "/cat - cat\n"
            "/challenge - challenge another player to rock/paper/scissors\n"
            "/diceroll - roll a die with the chosen amount of sides\n"
            "/dog - dog\n"
            "/flip - flip a coin\n"
            "/play - play rock/paper/scissors vs the bot\n"
            "/redeem - redeem rewards\n"
        ]
        # sends every command in the list in a message to the user
        await interaction.response.send_message(commands_list, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))