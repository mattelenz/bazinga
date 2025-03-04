import random
from discord.ext import commands
from discord import app_commands
import discord

class BlackjackView(discord.ui.View):
    def __init__(self, player, player_hand, dealer_hand, deck, bet, db_cog, bot):
        super().__init__(timeout=60)
        self.player = player
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.deck = deck
        self.bet = bet
        self.db_cog = db_cog
        self.message = None
        self.bot = bot

    def calculate_hand(self, hand):
        total = 0
        aces = 0
        card_values = {
            '2':2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        for card in hand:
            value = card.split(" ")[0]
            total += card_values[value]
            if value == 'A':
                aces += 1

        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        return total
    
    async def end_game(self, interaction, result_message, announce_result=True):
        
        for child in self.children:
            child.disabled = True
        
        try:
            await interaction.edit_original_response(content=result_message, view=self)
        
        except Exception as e:
            print(f"Error updating response: {e}")
            
            if self.message:
                await self.message.edit(content=result_message, view=self)
        
        if announce_result:
            result_summary = result_message.split('!')[0] + '!'
            
            try:
                channel_id = interaction.channel.id
                channel = self.player.guild.get_channel(channel_id) or await self.player.guild.fetch_channel(channel_id)
                
                if channel:
                    if "won" in result_summary.lower() or "win" in result_summary.lower():
                        bet_result = f"+{self.bet}"
                    elif "lost" in result_summary.lower() or "lose" in result_summary.lower():
                        bet_result = f"-{self.bet}"
                    else:
                        bet_result = f"{self.bet}"
                    await channel.send(
                        f"**Blackjack Results**\n"
                        f"{self.player.mention} {result_summary} {bet_result} $GBP.",
                    )

                else:
                    print(f"Could not find channel with ID {channel_id}")

            except Exception as e:
                print(f"Error sending announcement: {e}")

        self.stop()

    async def on_timeout(self):
        player_total = self.calculate_hand(self.player_hand)
        dealer_total = self.calculate_hand(self.dealer_hand)

        for child in self.children:
            child.disabled = True

        self.db_cog.update_currency(self.player.id, 0)

        try:
            await self.message.edit(
                content=f"Game timed out! No $GBP was lost.\n"
                        f"Your hand: {', '.join(self.player_hand)} (Total: {player_total})\n"
                        f"Dealer's hand: {', '.join(self.dealer_hand)} (Total: {dealer_total})",
                view=self
            )
        except:
            pass

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        self.player_hand.append(self.deck.pop())
        total = self.calculate_hand(self.player_hand)

        if total > 21:
            self.db_cog.update_currency(self.player.id, -self.bet)
            await self.end_game(interaction, f"You busted! Your hand: {', '.join(self.player_hand)} (Total: {total})\nDealer wins!", True)
        else:
            await interaction.edit_original_response(
                content=f"Your hand: {', '.join(self.player_hand)} (Total: {total})\n"
                        f"Dealer's hand: {self.dealer_hand[0]}, [Hidden card]",
                view=self
            )

    @discord.ui.button(label='Stand', style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        while self.calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.pop())

        dealer_total = self.calculate_hand(self.dealer_hand)
        player_total = self.calculate_hand(self.player_hand)

        if dealer_total > 21 or player_total > dealer_total:
            self.db_cog.update_currency(self.player.id, self.bet)
            result = f"You win! Your hand: {', '.join(self.player_hand)} (Total: {player_total})\n" \
                     f"Dealer's hand: {', '.join(self.dealer_hand)} (Total: {dealer_total})"
        elif player_total < dealer_total:
            self.db_cog.update_currency(self.player.id, -self.bet)
            result = f"You lose! Your hand: {', '.join(self.player_hand)} (Total: {player_total})\n" \
                     f"Dealer's hand: {', '.join(self.dealer_hand)} (Total: {dealer_total})"
        else:
            result = f"It's a tie! Your hand: {', '.join(self.player_hand)} (Total: {player_total})\n" \
                     f"Dealer's hand: {', '.join(self.dealer_hand)} (Total: {dealer_total})"
        
        await self.end_game(interaction, result, True)

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f"{value} of {suit}" for value in values for suit in suits]
        random.shuffle(deck)
        return deck

    def calculate_hand(self, hand):
        total = 0
        aces = 0
        card_values = {
            '2':2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
            'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }
        for card in hand:
            value = card.split(" ")[0]
            total += card_values[value]
            if value == 'A':
                aces += 1

        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        return total
    
    @app_commands.command(name="blackjack", description="Play a game of blackjack against the bot!")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        db_cog = self.bot.get_cog("DatabaseCog")
        if not db_cog:
            await interaction.response.send_message("Database cog not loaded", ephemeral=True)
            return
        
        user_currency = db_cog.get_currency(interaction.user.id)
        if bet > user_currency:
            await interaction.response.send_message("You don't have enough $GBP to place that bet! Use /balance to find out how much you have.", ephemeral=True)
            return
        
        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        view = BlackjackView(interaction.user, player_hand, dealer_hand, deck, bet, db_cog, self.bot)

        await interaction.response.send_message(
            f"Your hand: {', '.join(player_hand)} (Total: {self.calculate_hand(player_hand)})\n"
            f"Dealer's hand: {dealer_hand[0]}, [Hidden card]",
            view = view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Blackjack(bot))