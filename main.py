import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load bot token from somewhere safe (a hidden env file)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
if not TOKEN:
    raise ValueError("No token found.")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# message the terminal when successfully logged in
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    await load_extension()
    # sync extensions with discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
    # error check
    except discord.errors.DiscordException as e:
        print(f"Discord error syncing commands: {e}")
    except Exception as e:
        print(f"Error syncing commands: {e}")


# load cog files
async def load_extension():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = filename[:-3]
            if cog_name in bot.cogs:
                print(f'{cog_name} is already loaded.')
            else:
                try:
                    await bot.load_extension(f'cogs.{cog_name}')
                    print(f'Loaded extension {cog_name}.')
                # error check
                except Exception as e:
                    print(f'Failed to load extension {cog_name}: {e}')

# run the bot
async def main():
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("Shutting down bot...")
        await bot.close()
    # this takes all the errors that pop up when using ctrl + c to shutdown the bot and packs them away neatly
    except asyncio.CancelledError:
        print("Tasks cancelled during shutdown.")
    finally:
        print("Bot has been shut down.")

if __name__ == "__main__":
    asyncio.run(main())