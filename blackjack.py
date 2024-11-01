import random
import time

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
        print("The deck is empty. Reshuffling deck...")
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
        bet = input("How many chips would you like to bet? (A for All-in)")
        if bet.upper() == 'A':
            print(f"\nBET: {chips} Chips")
            time.sleep(1)
            return chips
        try:
            bet = int(bet)
            if bet <= 0:
                print("Bet must be greater than zero. Please enter a valid amount.")
                continue
            if bet <= chips:
                print(f"\nBET: {bet} Chips")
                time.sleep(1)
                return bet
            print(f"Sorry, you don't have enough chips. You have {chips} chips.")
        except ValueError:
            print("Invalid input. Please enter a number or 'A'.")

def deal_cards():
    """Deal two initial cards to both dealer and player."""
    dealer_hand = [gen_card(), gen_card()]
    player_hand = [gen_card(), gen_card()]
    
    return dealer_hand, player_hand

def check_21(player_hand, round):
    print(f"\nYour hand: {', '.join(player_hand)} ", end='')
    if round == 1:
        print("(blackjack)")
        time.sleep(1)
        print("Blackjack! Standing!")
        time.sleep(1)
        player_blackjack = True
    else:
        print("(total: 21)")
        time.sleep(1)
        print("Hand reached 21! Standing...")
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

    print(f"\nYour hand: {', '.join(player_hand)} (total: {total}{soft})")
    print(f"Dealer's hand: [?], {dealer_hand[1]}\n")

    # Provide choices: hit, stand, or split and or double down
    print("\nWould you like to:\n• HIT (h)\n• STAND (s)")
    if player_hand[0] == player_hand[1] and round == 1:  # SPLIT only available in round 1 and if hand cards match
        print("• SPLIT (sp)")
    if bet <= chips / 2:  # Only allow double down if player betted less than half their chips
        print("• DOUBLE DOWN (d)")

    while True:
        choice = input("Choice: ").lower()
        if choice in ['h', 's']:
            break
        if choice == 'd' and bet <= chips / 2:
            break
        if choice == 'sp' and player_hand[0] == player_hand[1] and round == 1:
            print("SPLIT feature not yet implemented.")  # Placeholder for future implementation
            return  # Just return, not implemented yet
        print("\nInvalid input, try again.\n")

    if choice == 'h':
        player_hand.append(gen_card())  # Add a new card to player's hand
        print(f"\nYou got a {player_hand[-1]}!")
        time.sleep(1)

        total, soft = calculate_hand(player_hand)
        if total > 21:  # Check if player is bust after hit
            print(f"Your hand: {', '.join(player_hand)} (total: {total}{soft})")
            time.sleep(1)
            return -1  # Dealer wins if player is bust

    elif choice == 's':
        # Dealer plays if player stands; return outcome
        return dealer_play(dealer_hand, player_hand, False)

    elif choice == 'd':
        bet *= 2  # Double the player's bet

        print(f"\nDouble Down! Your new bet is {bet} chips.")
        time.sleep(1)
        player_hand.append(gen_card())  # Deal one more card
        print(f"\nYou got a {player_hand[-1]}!")
        time.sleep(1)
        total, soft = calculate_hand(player_hand)
        if total > 21:  # Check if player busts
            print(f"Your hand: {', '.join(player_hand)} (total: {total}{soft})")
            time.sleep(1)
            return -1  # Dealer wins if player busts
        else:
            # Immediately pass to dealer's play since double down ends player's turn
            return dealer_play(dealer_hand, player_hand, False)

def dealer_play(dealer_hand, player_hand, player_blackjack):
    """Simulate dealer's turn."""
    dealer_total, dealer_soft = calculate_hand(dealer_hand)  # Get dealer's hand total
    player_total, _ = calculate_hand(player_hand)  # Get player's hand total

    print(f"\nDealer's hand: {', '.join(dealer_hand)} (total: {dealer_total}{dealer_soft})")
    time.sleep(1)
    
    while dealer_total < 17 or (dealer_total == 17 and 'soft' in dealer_soft):  # Dealer must hit if total is less than 17
        dealer_hand.append(gen_card())
        dealer_total, dealer_soft = calculate_hand(dealer_hand)  # Get dealer's hand total
        print(f"\nThe Dealer got a {dealer_hand[-1]}!")
        print(f"Dealer's hand: {', '.join(dealer_hand)} (total: {dealer_total}{dealer_soft})")
        time.sleep(2)

    if dealer_total > 21:
        if player_blackjack:
            return 3 # Player wins with blackjack
        return 1  # Dealer busts, player wins

    # Determine outcome based on final totals
    time.sleep(1)
    print(f"Checking the dealer's hand ({dealer_total}) against your hand ({player_total})...")
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

    while total > 21 and ace_count > 0: # Convert as much aces as needed to 1 to keep total < 21
        total -= 10
        ace_count -= 1
    # If player has an ace, total not over 21 and there are still aces to convert, count as soft
    soft = ' soft' if 'ACE' in hand and total <= 21 and ace_count else ''
    return total, soft

bet = 0
def main():
    global bet
    """Main game function."""
    chips = 100  # Initial chip count
    while True:  # Loop to play multiple rounds
        if chips == 0:
            print("\nYou're out of chips! Better luck next time!")
            break
        print(f"You have {chips} chips!\n")
        bet = place_bet(chips)  # Player places bet
        dealer_hand, player_hand = deal_cards()  # Deal initial hands

        round = 1
        while True:
            state = play(player_hand, dealer_hand, round, chips)  # Play round
            round += 1  # Increment round count for split tracking

            if state == -2:
                print(f"\nYou lost {bet} chips!\n")
                chips -= bet  # Deduct bet from chips
                break
            if state == -1:
                print("\nYou BUSTED!")  # Player lost, busts
                print(f"You lost {bet} chips!\n")
                chips -= bet  # Deduct bet from chips
                break
            if state == 0:
                print("\nTie!")  # TieIt's a tie!")
                print(f"You get your {bet} chips back!\n")
                break
            if state == 1:
                print("\nThe Dealer BUSTED!")  # Player wins if dealer busts
                print(f"You won {bet} chips!\n")
                chips += bet  # Add bet to chips
                break
            if state == 2:
                print(f"\nYou won {bet} chips!\n")
                chips += bet  # Add bet to chips
                break
            if state == 3:
                print(f"\nBlackjack! You won {int(bet * 1.5)} chips!\n")
                chips += int(bet * 1.5)  # add 1.5x the bet
                break

        # Check if player wants to continue after each round
        replay = input("Would you like to play again? (Y/n)").lower()
        if replay == 'n':
            break  # Exit the game

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
