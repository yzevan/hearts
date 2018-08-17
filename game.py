from card import Suit, Rank, Card, Deck
from rules import is_card_valid, count_points, all_valid_cards
from players.montecarlo_player import MonteCarloPlayer
import variables
import logging


class Game:

    def __init__(self, players = None, game_nr = 0):
        """
        players is a list of four players
        """
        self.verbose = variables.verbose_game
        self.players = players
        self.game_nr = game_nr
        self.player_hands = [[], [], [], []]
        self.cards_taken = ([], [], [], [])
        self.current_player_index = 0
        self.current_trick_valid_cards = []
        self.cards_played = ()
        self.current_trick = []
        self.trick_nr = 0
        self.leading_index = 0
        self.exposed = False
        self.are_hearts_broken = False
        self.is_spade_queen_played = False
        self.round_players = []
        self.out_of_suits = {}
        for i in range(4):
            self.out_of_suits[i] = {Suit.clubs: False, Suit.diamonds: False, Suit.spades: False, Suit.hearts: False}
        if players:
            self.new_game()

    def say(self, message, *formatargs):
        if self.verbose:
            logging.debug(message.format(*formatargs))

    def new_game(self):
        deck = Deck()
        self.player_hands = list(deck.deal())
        for i, player in enumerate(self.players):
            player.setIndex(i)

    def set_attributes(self, current_trick, player_hands, cards_played, are_hearts_broken, is_spade_queen_played, current_player_index, leading_index, cards_taken, round_players, trick_nr):
        self.current_trick = current_trick
        self.player_hands = player_hands
        self.cards_played = cards_played
        self.are_hearts_broken = are_hearts_broken
        self.is_spade_queen_played = is_spade_queen_played
        self.current_player_index = current_player_index
        self.leading_index = leading_index
        self.cards_taken = cards_taken
        self.round_players
        self.trick_nr = trick_nr

    def play(self):
        """
        Simulate a single game and return a 4-tuple of the scores.
        """
        # Players and their hands are indentified by indices ranging from 0 till 4

        # Perform the card passing.
        self.card_passing()
        self.exposing()

        # Play the tricks
        self.leading_index = self.player_index_with_two_of_clubs()
        self.current_player_index = self.leading_index
        self.round_players = [(self.leading_index + i) % 4 for i in range(4)]    
        self.current_trick_valid_cards = all_valid_cards(self.player_hands[self.current_player_index], self.current_trick, self.trick_nr, self.are_hearts_broken)
        for _ in range(13):
            self.play_trick()

        results = count_points(self.cards_taken, self.exposed)
        # Print and return the results
        self.say('Results of this game:')
        for i in range(4):
            self.say('Player {} got {} points from the cards {}',
                     i,
                     results[i],
                     ' '.join(str(card) for card in self.cards_taken[i])
                     )

        return tuple(results)

    def exposing(self):
        for i in range(4):
            if Card(Suit.hearts, Rank.ace) in self.player_hands[i]:        
                self.exposed = self.players[i].expose()
                return

    def card_passing(self):
        """
        Perform the card passing.
        """
        if self.game_nr in [1, 2, 3]:
            cards_to_pass = [[], [], [], []]
            for i in range(4):
                cards_to_pass[i] = self.players[i].pass_cards(self.player_hands[i])
            for i in range(4):
                for card in cards_to_pass[i]:
                    if self.game_nr == 1:
                        self.player_hands[i].remove(card)
                        self.player_hands[(i + 1) % 4].append(card)
                    elif self.game_nr == 2:
                        self.player_hands[i].remove(card)
                        self.player_hands[(i + 3) % 4].append(card)
                    elif self.game_nr == 3:
                        self.player_hands[i].remove(card)
                        self.player_hands[(i + 2) % 4].append(card)
            for i in range(4):
                self.player_hands[i].sort()

    def play_trick(self):
        """
        Simulate a single trick.
        leading_index contains the index of the player that must begin.
        """
        for _ in range(4):
            self.step()

    def step(self):
        player = self.players[self.current_player_index]
        if type(player) == MonteCarloPlayer:
            player = MonteCarloPlayer()
            player.setGame(self)
            player.setIndex(self.current_player_index)
        remaining_players = self.round_players[((self.round_players.index(self.current_player_index) + 1) % 4):]
        played_card = player.play_card(self.current_trick_valid_cards, self.current_trick, self.out_of_suits, remaining_players, self.are_hearts_broken, self.is_spade_queen_played)
        self.update_status(played_card)

    def update_status(self, played_card):
        self.current_trick.append(played_card)
        self.player_hands[self.current_player_index].remove(played_card)
        self.cards_played += (played_card,)
        if not self.are_hearts_broken and played_card.suit == Suit.hearts:
            self.are_hearts_broken = True
        if not self.is_spade_queen_played and played_card == Card(Suit.spades, Rank.queen):
            self.is_spade_queen_played = True
        self.current_player_index = (self.current_player_index + 1) % 4
        if len(self.current_trick) == 4:
            leading_suit = self.current_trick[0].suit
            for i in range(1, 4):
                if not self.out_of_suits[self.round_players[i]][leading_suit] and self.current_trick[i].suit != leading_suit:
                    self.out_of_suits[self.round_players[i]][leading_suit] = True
            winning_index = self.winning_index(self.current_trick)
            self.leading_index = self.round_players[winning_index]
            self.current_player_index = self.leading_index
            # self.say('Player {} won the trick {}.', self.leading_index, self.current_trick)
            self.cards_taken[self.leading_index].extend(self.current_trick)
            # self.say('Cards played: {}', self.cards_played)
            self.round_players = [(self.leading_index + i) % 4 for i in range(4)]
            self.current_trick = []
            self.trick_nr += 1
        self.current_trick_valid_cards = all_valid_cards(self.player_hands[self.current_player_index], self.current_trick, self.trick_nr, self.are_hearts_broken)
            
    def player_index_with_two_of_clubs(self):
        two_of_clubs = Card(Suit.clubs, Rank.two)
        for i in range(4):
            if two_of_clubs in self.player_hands[i]:
                return i

    def winning_index(self, trick):
        """
        Determine the index of the card that wins the trick.
        trick is a list of four Cards, i.e. an entire trick.
        """
        leading_suit = trick[0].suit
        result = 0
        result_rank = Rank.two
        for i, card in enumerate(trick):
            if card.suit == leading_suit and card.rank > result_rank:
                result = i
                result_rank = card.rank
        return result

    def winners(self):
        if len(self.cards_played) != 52:
            return None
        winners = []
        results = count_points(self.cards_taken, self.exposed)
        min_point = min(results)
        for i in range(4):
            if results[i] == min_point:
                winners.append(i)
        return winners