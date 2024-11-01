import random
import time
from rich.console import Console
from rich.text import Text
from rich import print
import questionary

console = Console()
custom_style = questionary.Style([
    ('qmark', 'fg:#9968EE bold'),       # Question mark color
    ('question', 'fg:#82b0e1'),         # Question text color
    ('pointer', 'fg:#ff69b4 bold'),     # Pointer color
    ('highlighted', 'fg:#c4b4ed bold'), # Highlighted option color
])

# Card values: face cards are 10, ACE is 11 by default
cards = {
    'ACE': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
    '8': 8, '9': 9, '10': 10, 'JACK': 10, 'QUEEN': 10, 'KING': 10
}
deck = [
    'ACE', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'JACK', 'QUEEN', 'KING',
] * 4
random.shuffle(deck)

def gen_card():
    """Generate a random card"""
    global deck
    if len(deck) == 0:
        print("[yellow]The deck is empty. Reshuffling deck...[/]")
        time.sleep(1)
        deck = [
            'ACE', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'JACK', 'QUEEN', 'KING',
        ] * 4
        random.shuffle(deck)

    card = deck.pop()
    return card

def place_bet(chips):
    """Allow player to place a bet within available chip count."""
    while True:
        bet = questionary.text(
            "How many chips would you like to bet? (A for All-in)",
            style=custom_style
        ).ask()
        if bet.upper() == 'A':
            print(f"\n[bold green]BET:[/] {chips} Chips")
            time.sleep(1)
            return chips
        try:
            bet = int(bet)
            if bet <= 0:
                print("[red]Bet must be greater than zero. Please enter a valid amount.[/]")
                continue
            if bet <= chips:
                print(f"\n[bold green]BET:[/] {bet} Chips")
                time.sleep(1)
                return bet
            print(f"[red]Sorry, you don't have enough chips. You have {chips} chips.[/]")
        except ValueError:
            print("[red]Invalid input. Please enter a number or 'A'.[/]")

def deal_cards():
    """Deal two initial cards to both dealer and player."""
    dealer_hand = [gen_card(), gen_card()]
    player_hand = [gen_card(), gen_card()]
    
    return dealer_hand, player_hand

def check_21(player_hand, round):
    print(f"\n[bold magenta]Your hand:[/] {', '.join(player_hand)} ", end='')
    if round == 1:
        print("(blackjack)")
        time.sleep(1)
        print("[bold green]Blackjack! Standing![/]")
        time.sleep(1)
        player_blackjack = True
    else:
        print("(total: 21)")
        time.sleep(1)
        print("[bold green]Hand reached 21! Standing...[/]")
        time.sleep(1)
        player_blackjack = False

    return player_blackjack


def play(player_hand, dealer_hand, round, chips):
    global bet
    """Handle the player's turn and game choices."""
    total, soft = calculate_hand(player_hand)  # Calculate current hand total and softness (ACE adjustment)

    if total == 21:
        player_blackjack = check_21(player_hand, round)
        return dealer_play(dealer_hand, player_hand, player_blackjack)

    print(f"\n[bold magenta]Your hand:[/] {', '.join(player_hand)} (total: {total}{soft})")
    print(f"[bold magenta]Dealer's hand:[/] [?], {dealer_hand[1]}\n")

    # Provide choices: hit, stand, or split if first round and cards are the same
    choices = ["HIT", "STAND"]
    if player_hand[0] == player_hand[1] and round == 1:
        choices.append("SPLIT")
    if bet <= chips / 2:
        choices.append("DOUBLE DOWN")

    choice = questionary.select(
        "Would you like to:", choices=[choice for choice in choices],
        style=custom_style
    ).ask().lower()

    if choice == 'hit':
        player_hand.append(gen_card())  # Add a new card to player's hand
        print(f"\nYou got a {player_hand[-1]}!")
        time.sleep(1)

        total, soft = calculate_hand(player_hand)
        if total > 21:  # Check if player is bust after hit
            print(f"[bold magenta]Your hand:[/] {', '.join(player_hand)} (total: {total}{soft})")
            time.sleep(1)
            return -1  # Dealer wins if player is bust

    elif choice == 'stand':
        # Dealer plays if player stands; return outcome
        return dealer_play(dealer_hand, player_hand, False)

    elif choice == 'double down':
        bet *= 2  # Double the player's bet

        print(f"\n[bold green]Double Down! Your new bet is {bet} chips.[/]")
        time.sleep(1)
        player_hand.append(gen_card())  # Deal one more card
        print(f"\nYou got a {player_hand[-1]}!")
        time.sleep(1)
        total, soft = calculate_hand(player_hand)
        if total > 21:  # Check if player busts
            print(f"[bold magenta]Your hand:[/] {', '.join(player_hand)} (total: {total}{soft})")
            time.sleep(1)
            return -1  # Dealer wins if player busts
        else:
            # Immediately pass to dealer's play since double down ends player's turn
            return dealer_play(dealer_hand, player_hand, False)

def dealer_play(dealer_hand, player_hand, player_blackjack):
    """Simulate dealer's turn."""
    dealer_total, dealer_soft = calculate_hand(dealer_hand)  # Get dealer's hand total
    player_total, _ = calculate_hand(player_hand)  # Get player's hand total

    print(f"\n[bold magenta]Dealer's hand:[/] {', '.join(dealer_hand)} (total: {dealer_total}{dealer_soft})")
    time.sleep(1)
    
    while dealer_total < 17 or (dealer_total == 17 and 'soft' in dealer_soft):  # Dealer must hit if total is less than 17
        dealer_hand.append(gen_card())
        dealer_total, dealer_soft = calculate_hand(dealer_hand)  # Get dealer's hand total
        print(f"\nThe Dealer got a {dealer_hand[-1]}!")
        print(f"[bold magenta]Dealer's hand:[/] {', '.join(dealer_hand)} (total: {dealer_total}{dealer_soft})")
        time.sleep(2)

    if dealer_total > 21:
        if player_blackjack:
            return 3 # Player wins with blackjack
        return 1  # Dealer busts, player wins

    # Determine outcome based on final totals
    time.sleep(1)
    print(f"[bold yellow]Checking the dealer's hand ({dealer_total}) against your hand ({player_total})[/]...")
    time.sleep(2)

    if dealer_total > player_total:
        return -2 # Dealer wins by higher value
    elif dealer_total < player_total and player_blackjack:
        return 3 # Player wins with blackjack
    elif dealer_total < player_total:
        return 2 # Player wins by higher value
    else:
        return 0 # Tie

def calculate_hand(hand):
    """Calculate hand total and adjust for Aces if necessary."""
    total = sum(cards[card] for card in hand)  # Sum the values of the cards in hand
    ace_count = hand.count('ACE')

    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1

    # If player has an ace, total not over 21 and there are still aces to convert, count as soft
    soft = ' soft' if 'ACE' in hand and total <= 21 and ace_count else ''
    return total, soft

bet = 0
def main():
    print("[bold #ffffff]╔═══════════════╗\n║   BLACKJACK   ║\n╚═══════════════╝[/]\n")
    global bet
    """Main game function."""
    chips = 100  # Initial chip count
    while True:  # Loop to play multiple rounds
        if chips == 0:
            print("\n[bold red]You're out of chips! Better luck next time![/]")
            break
        print(f"You have {chips} chips!\n")
        bet = place_bet(chips)  # Player places bet
        dealer_hand, player_hand = deal_cards()  # Deal initial hands

        round = 1
        while True:
            state = play(player_hand, dealer_hand, round, chips)  # Play round
            round += 1  # Increment round count for split tracking

            if state == -2:
                print(f"\n[bold red]You lost {bet} chips![/]\n")
                chips -= bet  # Deduct bet from chips
                break
            if state == -1:
                print("\n[bold red]You BUSTED![/]")  # Player lost, busts
                print(f"[bold red]You lost {bet} chips![/]\n")
                chips -= bet  # Deduct bet from chips
                break
            if state == 0:
                print("\n[bold yellow]Tie![/]")  # TieIt's a tie!")
                print(f"[bold yellow]You get your {bet} chips back![/]\n")
                break
            if state == 1:
                print("\n[bold green]The Dealer BUSTED![/]")  # Player wins if dealer busts
                print(f"[bold green]You won {bet} chips![/]\n")
                chips += bet  # Add bet to chips
                break
            if state == 2:
                print(f"\n[bold green]You won {bet} chips![/]\n")
                chips += bet  # Add bet to chips
                break
            if state == 3:
                print(f"\n[bold green]Blackjack! You won {int(bet * 1.5)} chips![/]\n")
                chips += int(bet * 1.5)  # add 1.5x the bet
                break

        # Check if player wants to continue after each round
        replay = questionary.select(
            "Would you like to play again?", choices=['YES', 'NO'],
            style=custom_style
        ).ask().lower()

        if replay == 'no':
            break  # Exit the game

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
