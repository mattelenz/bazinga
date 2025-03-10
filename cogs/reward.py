import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

rewards = {
    "Lethal Company": 0,
    "Streetcan": 0,
    "Dirt": 0,
    "Muted": 0
}

class RewardView(View):
    def __init__(self, rewards, interaction, db_cog):
        super().__init__()
        self.interaction = interaction
        self.db_cog = db_cog
        for reward, amount in rewards.items():
            button = Button(label=f"{reward} -- {amount} $GBP", style=discord.ButtonStyle.primary, custom_id=reward)
            button.callback = self.create_callback(reward, amount)
            self.add_item(button)

    def create_callback(self, reward, amount):
        async def callback(interaction: discord.Interaction):
            try:
                user_id = interaction.user.id
                current_balance = self.db_cog.get_currency(user_id)

                if current_balance >= amount:
                    self.db_cog.update_currency(user_id, -amount)
                    await interaction.response.edit_message(content=f"You have redeemed {reward} for {amount} $GBP", view=None)
                    await interaction.channel.send(f"{interaction.user.display_name} has redeemed {reward} for {amount} $GBP!")
                else:
                    await interaction.response.send_message(content="You don't have enough $GBP to redeem this reward. Peep sadgers.", ephemeral=True)
            except Exception as e:
                print(f"Error handling button interaction: {e}")
                await interaction.response.send_message(content="An error ocured while processing your request. Please try again later.", ephemeral=True)
        return callback
    

class RewardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @app_commands.command(name="redeem", description="Redeem rewards with your $GBP.")
    async def redeem(self, interaction: discord.Interaction):
        db_cog = self.bot.get_cog('DatabaseCog')
        if db_cog:
            view = RewardView(rewards, interaction, db_cog)
            await interaction.response.send_message("Choose a reward to redeem:", view=view, ephemeral=True)
        else:
            await interaction.response.send_message("Database not available.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(RewardCog(bot))
