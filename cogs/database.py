import sqlite3
from discord.ext import commands
from discord import app_commands
import discord
from dotenv import load_dotenv
import os

# load the user_id from env
load_dotenv()
owner_id = int(os.getenv('USER_ID'))

# load the cog so main can use it
class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    # start the database file and create a db if one doesn't exist
    def initialize_database(self):
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS members (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        member_id INTEGER UNIQUE NOT NULL,
                        currency INTEGER DEFAULT 0    
                            )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")

    # add a member to the database
    def add_member(self, member_id):
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO members (member_id) VALUES (?)', (member_id,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in update_currency (member_id: {member_id}): {e}")

    # update a member's currency
    def update_currency(self, member_id, amount):
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE members SET currency = currency + ? WHERE member_id = ?', (amount, member_id))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error in update_currency (member_id: {member_id}, amount: {amount}): {e}")

    # get a member's #GBP amount
    def get_currency(self, member_id):
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO members (member_id) VALUES (?)', (member_id,))
                cursor.execute('SELECT currency FROM members WHERE member_id = ?', (member_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Database error in get_currency: {e}")
            return 0

    # helper function for the award command
    def reward_user(self, member_id, amount):
        try:
            self.add_member(member_id)
            self.update_currency(member_id, amount)
            return self.get_currency(member_id)
        except Exception as e:
            print(f"Error in reward_user (member_id: {member_id}, amount: {amount}): {e}")
            return 0

    # balance slash command - lets a member check their balance
    @app_commands.command(name="balance", description="Check your current $GBP balance.")
    async def check_balance(self, interaction: discord.Interaction):
        member_id = interaction.user.id
        try:
            self.add_member(member_id)
            balance = self.get_currency(member_id)
            await interaction.response.send_message(f"You have {balance} $GBP!", ephemeral=True)
        except Exception as e:
            print(f"Error in /balance command for (member_id: {member_id}): {e}")
            await interaction.response.send_message("An error occured while retrieving your balance. Please try again later.", ephemeral=True)

    # award a member a set amount of $GBP
    @app_commands.command(name="award", description="Award some $GBP to a good boy.")
    @app_commands.describe(member="Which user was a good boy?")
    async def award_currency(self, interaction: discord.Interaction, member: discord.Member):
    
        reward_amount = 100

        if member.id == interaction.user.id:
            if interaction.user.id == owner_id:
                try:
                    new_balance = self.reward_user(member.id, reward_amount)
                    await interaction.response.send_message(
                        f"You've awarded yourself {reward_amount} #GBP.",
                        ephemeral=True
                    )

                    await interaction.followup.send(
                        f"Your new balance is {new_balance} #GBP!",
                        ephemeral=True
                    )
                except Exception as e:
                    print(f"Error in /award command for (member_id {member.id}: {e})")
                    await interaction.response.send_message("An error occured while awarding $GBP. Please try again later.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{interaction.user.display_name} tried to reward themselves with $GBP. Greedy.")
            return
        
        
        try:
            new_balance = self.reward_user(member.id, reward_amount)
            await interaction.response.send_message(
                f"{interaction.user.mention} has rewarded {member.mention} with {reward_amount} #GBP!"
            )

            await interaction.followup.send(
                f"Your new balance is {new_balance} $GBP!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error in /award command for (member_id {member.id}): {e}")
            await interaction.response.send_message("An error occured while awarding #GBP. Please try again later.", ephemeral=True)

    
async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))
