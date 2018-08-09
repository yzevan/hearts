from card import Suit, Rank, Card, Deck
from rules import is_card_valid, card_points
from players.montecarlo_player import MonteCarloPlayer

class Game:

    def __init__(self, players, game_nr, verbose=True):
        """
        players is a list of four players
        """
        self.verbose = verbose
        self.players = players
        self.game_nr = game_nr

        self.new_game()

    def say(self, message, *formatargs):
        if self.verbose:
            print(message.format(*formatargs))

    def new_game(self):
        deck = Deck()
        self.player_hands = tuple(deck.deal())
        self.cards_taken = ([], [], [], [])
        self.current_player_index = 0
        self.current_trick_valid_cards = []
        self.cards_played = ()
        self.current_trick = []
        self.trick_nr = 0
        self.leading_index = 0
        for i, player in enumerate(self.players):
            player.setIndex(i)

    def are_hearts_broken(self):
        """
        Return True if the hearts are broken yet, otherwise return False.
        """
        return any(card.suit == Suit.hearts for card in self.cards_played)

    def is_spade_queen_played(self):
        """
        Return True if the spade queen is played yet, otherwise return False.
        """
        return Card(Suit.spades, Rank.queen) in self.cards_played

    def play(self):
        """
        Simulate a single game and return a 4-tuple of the scores.
        """
        # Players and their hands are indentified by indices ranging from 0 till 4

        # Perform the card passing.
        self.card_passing()

        # Play the tricks
        self.leading_index = self.player_index_with_two_of_clubs()
        self.current_player_index = self.leading_index
        self.current_trick_valid_cards = self.players[self.current_player_index].all_valid_cards(self.player_hands[self.current_player_index], self.current_trick, self.trick_nr, self.are_hearts_broken())
        for _ in range(13):
            self.play_trick()

        results = self.count_points()
        # Print and return the results
        self.say('Results of this game:')
        for i in range(4):
            self.say('Player {} got {} points from the cards {}',
                     i,
                     results[i],
                     ' '.join(str(card) for card in self.cards_taken[i])
                     )

        return tuple(results)

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
                        self.player_hands[(i + 2) % 4].append(card)
                    elif self.game_nr == 3:
                        self.player_hands[i].remove(card)
                        self.player_hands[(i + 3) % 4].append(card)

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
            player.update(self.cards_played)
            player.setIndex(self.current_player_index)
        played_card = player.play_card(self.player_hands[self.current_player_index], self.current_trick, self.trick_nr, self.are_hearts_broken(), self.is_spade_queen_played())
        self.update_status(played_card)

    def update_status(self, played_card):
        self.current_trick.append(played_card)
        self.player_hands[self.current_player_index].remove(played_card)
        self.cards_played += (played_card,)
        self.current_player_index = (self.current_player_index + 1) % 4
        if len(self.current_trick) == 4:
            winning_index = self.winning_index(self.current_trick)
            self.leading_index = (self.leading_index + winning_index) % 4
            self.current_player_index = self.leading_index
            # self.say('Player {} won the trick {}.', self.leading_index, self.current_trick)
            self.cards_taken[self.leading_index].extend(self.current_trick)
            # self.say('Cards played: {}', self.cards_played)
            self.current_trick = []
            self.trick_nr += 1
        self.current_trick_valid_cards = self.players[self.current_player_index].all_valid_cards(self.player_hands[self.current_player_index], self.current_trick, self.trick_nr, self.are_hearts_broken())
            
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

    def count_points(self):
        """
        Count the number of points in cards, where cards is a list of Cards.
        """
        points = [0, 0, 0, 0]
        for i, cards in enumerate(self.cards_taken):
            points[i] = sum(card_points(card) for card in cards)
        for i, point in enumerate(points):
            if point == 26:
                self.say('Shoot the moon')
                for x in range(4):
                    points[x] = (0 if x == i else 26)
                return points
        return points

    def winners(self):
        if len(self.cards_played) != 52:
            return None
        winners = []
        results = self.count_points()
        min_point = min(results)
        for i in range(4):
            if results[i] == min_point:
                winners.append(self.players[i])
        return winners