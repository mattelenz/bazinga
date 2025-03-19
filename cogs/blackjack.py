import random
from discord.ext import commands
from discord import app_commands
import discord

# using View to add buttons to the messages
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

    # calculate the score for the current hand
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

        # deal with aces being 1 or 11
        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        return total
    
    # function to end the game and return text with the winner
    async def end_game(self, interaction, result_message, announce_result=True):
        
        # disables the chat buttons
        for child in self.children:
            child.disabled = True
        
        # edit the message with the game results
        try:
            await interaction.edit_original_response(content=result_message, view=self)
        
        except Exception as e:
            print(f"Error updating response: {e}")
            
            if self.message:
                await self.message.edit(content=result_message, view=self)
        
        if announce_result:
            result_summary = result_message.split('!')[0] + '!'
            
            # used a try here since there was an error with the bot not sending the message in the right channel
            try:
                channel_id = interaction.channel.id
                channel = self.player.guild.get_channel(channel_id) or await self.player.guild.fetch_channel(channel_id)
                
                # determine whether it was a win or loss and +/- currency
                if channel:
                    if "won" in result_summary.lower() or "win" in result_summary.lower():
                        bet_result = f"+{self.bet}"
                    elif "lost" in result_summary.lower() or "lose" in result_summary.lower() or "busted" in result_summary.lower():
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

    # making sure currency isn't lost if the game times out
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

    # hit ui button
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # if the user presses hit, pop a card off the stack
        self.player_hand.append(self.deck.pop())
        total = self.calculate_hand(self.player_hand)

        # determine a bust
        if total > 21:
            self.db_cog.update_currency(self.player.id, -self.bet)
            await self.end_game(interaction, f"You busted! Your hand: {', '.join(self.player_hand)} (Total: {total})\nDealer wins!", True)
        else:
            await interaction.edit_original_response(
                content=f"Your hand: {', '.join(self.player_hand)} (Total: {total})\n"
                        f"Dealer's hand: {self.dealer_hand[0]}, [Hidden card]",
                view=self
            )

    # stand ui button, works very much the same as Hit
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

# running the actual game
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # making a deck with our lists
    def create_deck(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f"{value} of {suit}" for value in values for suit in suits]
        random.shuffle(deck)
        return deck

    # calculates the hand, same logic as above
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
    
    # creating the blackjack slash command
    @app_commands.command(name="blackjack", description="Play a game of blackjack against the bot!")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        # load the db
        db_cog = self.bot.get_cog("DatabaseCog")
        # error check the db
        if not db_cog:
            await interaction.response.send_message("Database cog not loaded", ephemeral=True)
            return
        
        # get the user's currency amount
        user_currency = db_cog.get_currency(interaction.user.id)
        # error check the bet
        if bet > user_currency:
            await interaction.response.send_message("You don't have enough $GBP to place that bet! Use /balance to find out how much you have.", ephemeral=True)
            return
        
        # deal the cards
        deck = self.create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        # create the view to have buttons in the bot messages for hit/stand
        view = BlackjackView(interaction.user, player_hand, dealer_hand, deck, bet, db_cog, self.bot)

        # update the view to show the player's/bot's current standing
        await interaction.response.send_message(
            f"Your hand: {', '.join(player_hand)} (Total: {self.calculate_hand(player_hand)})\n"
            f"Dealer's hand: {dealer_hand[0]}, [Hidden card]",
            view = view,
            ephemeral=True
        )

        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(Blackjack(bot))