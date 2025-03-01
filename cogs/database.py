import sqlite3
from discord.ext import commands
from discord import app_commands
import discord

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER UNIQUE NOT NULL,
                currency INTEGER DEFAULT 0    
                       )
        ''')
        conn.commit()
        conn.close()

    def add_member(self, member_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO members (member_id) VALUES (?)' (member_id,))
        conn.commit()
        conn.close()

    def update_currency(self, member_id, amount):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE members SET currency = currency + ? WHERE member_id = ?', (amount, member_id))
        conn.commit()
        conn.close()

    def get_currency(self, member_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT currency FROM members WHERE member_id = ?', (member_id,))
        result = cursor.fetchone()
        conn.close
        return result[0] if result else 0

    def reward_user(self, member_id, amount):
        self.add_member(member_id)
        self.update_currency(member_id, amount)
        return self.get_currency(member_id)

    @app_commands.command(name="balance", description="Check your current coin balance.")
    async def check_balance(self, interaction: discord.interaction):
        member_id = interaction.user.id
        self.add_member(member_id)
        balance = self.get_currency(member_id)
        await interaction.response.send_message(f"You have {balance} coins!")

    @app_commands.command(name="award", description="Award some coins to a good boy.")
    @app_commands.describe(member="Which user was a good boy?")
    async def award_currency(self, interaction: discord.Interaction, member: discord.Member):
        if member.id == interaction.user.id:
            await interaction.response.send_message(f"{interaction.user.id} tried to reward themselves with currency. Greedy fuck.")
            return
        
        reward_amount = 100
        new_balance = self.reward_user(member.id, reward_amount)
        await interaction.response.send_message(
            f"{interaction.user.mention} has rewarded {member.mention} with {reward_amount} coins!"
        )

        await interaction.followup.send(
            f"Your new balance is {new_balance} coins!",
            ephemeral=True
        )

    
async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))
