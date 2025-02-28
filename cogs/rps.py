import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands





class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.choices = ["rock", "paper", "scissors", "fire", "sponge", "air", "water"]

#  ============================
#  START Rock Paper Scissors
#  ============================

    # pick winner function
    def pick_winner(self, player1_choice, player2_choice, player1_name, player2_name):
        # determine a tie
        if player1_choice == player2_choice:
            return(
                f"**{player1_name}** chose **{player1_choice}** and **{player2_name}** chose **{player2_choice}**.\n"
                f"**{player1_name}** and **{player2_name}** have tied!"
            )
        elif (
            # all win conditions for player1
            (player1_choice == "rock" and player2_choice in ["sponge", "scissors", "fire"]) or
            (player1_choice == "paper" and player2_choice in ["water", "rock", "air"]) or
            (player1_choice == "scissors" and player2_choice in ["air", "sponge", "paper"]) or
            (player1_choice == "fire" and player2_choice in ["paper", "sponge", "scissors"]) or
            (player1_choice == "sponge" and player2_choice in ["water", "air", "paper"]) or
            (player1_choice == "air" and player2_choice in ["water", "rock", "fire"]) or
            (player1_choice == "water" and player2_choice in ["rock", "fire", "scissors"])
        ):
            return (
                f"**{player1_name}** chose **{player1_choice}** and **{player2_name}** chose **{player2_choice}**.\n"
                f"**{player1_name}** wins against **{player2_name}**!"
            )
        else:
            # only option left is a player2 win
            return (
                f"**{player1_name}** chose **{player1_choice}** and **{player2_name}** chose **{player2_choice}**.\n"
                f"**{player2_name}** wins against **{player1_name}**!"
            )


    # connect the cog to the bot(main)

    # define vs. bot slash command
    @app_commands.command(name="play", description="Play 7 choice rock/paper/scissors against the bot.")
    @app_commands.describe(choice="Your choice: rock, paper, scissors, fire, sponge, air, or water.")
    async def play(self, interaction: discord.Interaction, choice: str):
        # cast to lower to avoid case sensitivity
        choice = choice.lower()

        # make sure the user chose a real option
        if choice not in self.choices:
            await interaction.response.send_message("Invalid choice! Choose rock, paper, scissors, fire, sponge, air, or water.", ephemeral=True)
            return
        # randomize a bot choice
        bot_choice = random.choice(self.choices)
        # pass variable to winner function to pick a winner
        bot_winner = self.pick_winner(choice, bot_choice, interaction.user.display_name, self.bot.user.display_name)
        # post the winner
        await interaction.response.send_message(bot_winner)

    # define vs. player slash command
    @app_commands.command(name="challenge", description="Play 7 choice rock/paper/scissors against another player")
    @app_commands.describe(opponent="The user you want to challenge", choice="Your choice: rock, paper, scissors, fire, sponge, air , or water")
    async def challenge(self, interaction: discord.Interaction, opponent: discord.Member, choice: str):
        # cast to lower to avoid case sensitivity
        choice = choice.lower()

        # make sure the user chose a real option
        if choice not in self.choices:
            await interaction.response.send_message("Invalid choice! Choose rock, paper, scissors, fire, sponge, air, or water.", ephemeral=True)
            return
        
        # sends a message to the opponent
        await interaction.response.send_message(
            f"{interaction.user.mention} has challenged {opponent.mention} to rock/paper/scissors! "
            f"{opponent.mention}, type your choice ( 'rock', 'paper', 'scissors', 'fire', 'sponge', 'air', or 'water')."
        )

        # make sure the opponent chose a real option
        def check(message):
            return message.author == opponent and message.content.lower() in self.choices and message.channel == interaction.channel
        try:
            opponent_choice_msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            opponent_choice = opponent_choice_msg.content.lower()
        except asyncio.TimeoutError:
            await interaction.followup.send(f"{opponent.mention} took too long to respond. Challenge canceled.")
            return
        
        # determine the winner
        result = self.pick_winner(choice, opponent_choice, interaction.user.display_name, opponent.display_name)

        # send the winner
        await interaction.followup.send(result)

#  ============================
#  END Rock Paper Scissors
#  ============================

async def setup(bot):
    await bot.add_cog(RPS(bot))