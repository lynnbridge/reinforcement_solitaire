from matplotlib.pyplot import plasma
from card_elements import Pile, Suit, Card
import numpy as np
import math

class Game:
    
    """
    Description:
        A random game of solitaire is displayed for the agent.
        
        Observation:
            Num     Observation 
            0       Pile 1
            1       Pile 2
            2       Pile 3
            3       Pile 4
            4       Pile 5
            5       Pile 6
            6       Pile 7
            7       Deck
            8       Discard
            9       Foundation 1
            10      Foundation 2
            11      Foundation 3
            12      Foundation 4
          
        Not really sure I need this...
        Categories:
            Num     Action
            0       Pile to pile
            1       Deck to discard
            2       Discard to pile
            3       Discard to foundation
            4       Pile to foundation
            5       Flip card
            6       Discard to deck
            7       Foundation to pile
            
        Reward:
            "win": 1,
            "invalid_move": -1,
            "discard_pile": .1,
            "pile_foundation": .1,
            "foundation_pile": .01,
            "discard_deck": .01,
            "deck_discard": .1,
            "pile_pile": .1
        
        Episode Termination:
            When the episode length is greater than 500
            When the game is won
    """
    
    actual_scoring = {
        "discard_pile": 5, # deck to pile
        "discard_foundation": 10, # deck to foundation
        "pile_foundation": 10, # pile to foundation
        "flip": 5, # pile flip
        "foundation_pile": -15, # foundation to pile
        "deck_reset": -10, # deck flip over Done
        "deck_draw": 0, # draw from deck Done
        "pile_pile": 0, # Pile to pile
    }
    
    def __init__(self):
        self.state = []
        self.action_space = 97
        self.observation_space = []
        self.count = 0
        
        self.values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    
        self.suits = [ #keys are unicode symbols for suits
            Suit(u'\u2660', "black", "spade"),
            Suit(u'\u2665', "red", "heart"),
            Suit(u'\u2663', "black", "club"),
            Suit(u'\u2666', "red", "diamond"),
        ]
        
        self.reward = {
            "win": 1,
            "discard_pile": .1,
            "pile_foundation": .1,
            "foundation_pile": .01,
            "discard_deck": .01,
            "deck_discard": .1,
            "pile_pile": .1
        }
        
    def reset(self):
        # Initial state
        self.state = []
        self.observation_space = np.ndarray((97,), dtype="object")
        deck = Pile()
        self.count = 0
        deck.populate(self.values,self.suits)
        deck.shuffle()
        for i in range(7):
            tempPile = Pile()
            [tempPile.insert_card(deck.remove_card()) for j in range(i+1)]
            tempPile.flip_top_card()  
            self.state.append(tempPile)
        self.state.append(deck)
        for i in range(0,5):
            self.state.append(Pile())
        self.update_observation()
        return np.asarray(self.observation_space)
            
    def update_observation(self):
        # for spot in self.observation_space:
        it = np.nditer(self.observation_space, flags=['refs_ok', 'c_index'])
        while not it.finished:
            # Play Pile will go from 0 - 6
            for pile in range(0, 7, 1):
                # Observation space goes to 13 max cards
                for card in range(0, 13, 1):
                    if card < len(self.state[pile].cards) and self.state[pile].cards[card] is not None and self.state[pile].cards[card].flipped:
                        # print(self.state[pile].cards[card])
                        self.observation_space[it.index] = self.state[pile].cards[card]
                    it.iternext()                        
            # Deck
            if len(self.state[7].cards) > 0:
                self.observation_space[it.index] = Card(empty=False)
            else:
                self.observation_space[it.index] = Card()
            it.iternext()
            # Discard
            if len(self.state[8].cards) > 0:
                self.observation_space[it.index] = self.state[8].cards[0]
            else:
                self.observation_space[it.index] = Card()
            it.iternext()
            # Foundations 
            for pile in range(9, 13, 1):
                if len(self.state[pile].cards) > 0:
                    self.observation_space[it.index] = self.state[pile].cards[0]
                else:
                    self.observation_space[it.index] = Card()
                it.iternext()

    def step(self, action):        
        if self.check_if_completed():
            print("You won!")
            reward = 1
            done = True
            return np.array(self.observation_space), reward, done, {}
        else:
            done = False
            
        action = self.translate_action(action)
        
        move = self.assign_action(action)

        if not self.valid_action(action, move):
            # If NN stops learning, end game instead of returning -1   
            return np.array(self.observation_space), -1, done, {}
            
        # print("Move", move)
        
        reward = self.move_cards(action, move)
        
        self.update_observation()        
        
        return np.asarray(self.observation_space), reward, done, {}
    
    def translate_action(self, action):
        current = self.number_to_location(action['current_location'])
        next_loc = self.number_to_location(action['next_location'])
        number = self.cards_to_move(current, action['current_location'])
        
        return {
            'current_location': current,
            'next_location': next_loc,
            'number': number
        }
        
    def number_to_location(self, number):
        if number < 91:
            return math.floor(number/13)
        elif number == 91:
            return 7
        elif number == 92:
            return 8
        elif number == 93:
            return 9
        elif number == 94:
            return 10
        elif number == 95:
            return 11
        else:
            return 12
            
    def cards_to_move(self, current, location):
        playable_cards = self.get_playable_count(current)
        if playable_cards == 0:
            return 0
        if location > 90:
            return playable_cards
        count = 0
        for val in range(location, (current+1)*13):
            if self.observation_space[val] is not None and \
                not self.observation_space[val].empty:
                count+=1
        return count
    
    def get_game_elements(self):
        return_object = {
            "deck": str(self.state[7]),
            "discard": str(self.state[8]),
            "play_piles": [str(self.state[pile]) for pile in range(0, 7)],
            "foundations": [str(self.state[suit]) for suit in range(9, 13)]
        }
        return return_object
    
    def print_in_order(self):
        for i in range(0, len(self.state)):
            print(self.state[i])
        
    def valid_action(self, action, move):
        
        # Cannot do move that is not found in reward
        if move not in self.reward.keys():
            return False
        
        # print("Action:",action)
        # Cannot move cards that don't exist
        # print(len(self.state[action['current_location']].cards))
        if len(self.state[action['current_location']].cards) == 0:
            return False
        
        # Cannot move cards that don't exist
        if action['number'] > len(self.state[action['current_location']].cards):
            return False
        
        # Invalid discard, deck rules
        if action['next_location'] == 7:
            if len(self.state[action['next_location']].cards) != 0 or action['current_location'] != 8:
                return False
            if len(self.state[action['current_location']].cards) == 0:
                return False
        
        # Cannot flip flipped up cards
        if action['current_location'] == action['next_location'] and \
            action['number'] == 1 and \
            self.state[action['current_location']].cards[0].flipped:
            return False

        # Cannot move face down cards
        for i in range(0, action['number']):
            if not self.flipped_up_cards(self.state[action['current_location']].cards[i]):
                return False
            
        # Cannot stack onto the deck or discard
        if action['next_location'] == 7 or \
            action['next_location'] == 8:
            return False 
        
        # Invalid foundation moves
        if action['next_location'] == 9 or \
            action['next_location'] == 10 or \
            action['next_location'] == 11 or \
            action['next_location'] == 12:
            # Cannot move more than one card to foundation
            if action['number'] != 1:
                return False
            # Cannot move incorrect colors/numbers to foundation
            bottom_card = self.state[action['current_location']].cards[0]
            return self.foundations_rule(action['next_location'],bottom_card)
        else:
            # Non-foundation moves
            
            bottom_card = self.state[action['current_location']].cards[action['number']-1]
            # Cannot stack onto blank spaces unless kings
            if len(self.state[action['next_location']].cards) == 0: 
                if not self.empty_piles_rule(bottom_card):
                    return False
                return True
                    
            top_card = self.state[action['next_location']].cards[0]
            # Cannot stack onto face down cards
            if not self.flipped_up_cards(top_card):
                return False
            
            # Cannot stack on same colors
            if not self.stacking_color_rule(bottom_card, top_card):
                return False
            
            # Cannot stack out of order
            if not self.stacking_number_rule(bottom_card, top_card):
                return False
                
        return True
           
    def assign_action(self, action):
        if action['current_location'] == action['next_location']:
            return "flip"
        if action['current_location'] >= 0 and action['current_location'] < 7:
            start = "pile"
        elif action['current_location'] == 7:
            start = "deck"
        elif action['current_location'] == 8:
            start = "discard"
        else:
            start = "foundation"
        if action['next_location'] >= 0 and action['next_location'] < 7:
            end = "pile"
        elif action['next_location'] == 8:
            end = "discard"
        elif action['next_location'] == 7:
            end = "deck"
        else: 
            end = "foundation"
        act = start + "_" + end
        # print("act", act)
        return act
        
    def move_cards(self, action, move):
        if move == "pile_pile":
            temp = []
            for card in range(0, action['number']):
                temp.append(self.state[action['current_location']].remove_card())
            for card in range(action['number'] - 1, -1, -1):
                self.state[action['next_location']].insert_card(temp[card])
                print("Moving card", str(temp[card].suit), temp[card].value," from ", action['current_location'], " to ", action['next_location'])
            if len(self.state[action['current_location']].cards) > 0 and not self.state[action['current_location']].cards[0].flipped:
                self.state[action['current_location']].cards[0].flip()
                card = self.state[action['current_location']].cards[0]
                print("Flipping card", card.suit, card.value)
        
        elif move == "flip":
            self.state[action['current_location']].cards[0].flip()
            card = self.state[action['current_location']].cards[0]
            print("Flipping card", card.suit, card.value)
            
        elif move == "deck_discard":
            temp = self.state[action['current_location']].draw_top_card()
            self.state[action['next_location']].insert_card(temp)
            print("Moving card", temp.suit, temp.value, " from Deck to ", action['next_location'])

        elif move == "discard_deck":
            self.state[action['next_location']].cards = self.state[action['current_location']].cards[::-1].flip()
            self.state[action['current_location']] = []
            print("Moving cards from Discard to Deck")

        else:
            temp = self.state[action['current_location']].remove_card()
            self.state[action['next_location']].insert_card(temp)
            print("Moving card", temp.suit, temp.value," from ", action['current_location'], " to ", action['next_location'])
            if len(self.state[action['current_location']].cards) > 0 and not self.state[action['current_location']].cards[0].flipped:
                    self.state[action['current_location']].cards[0].flip()
                    card = self.state[action['current_location']].cards[0]
                    print("Flipping card", card.suit, card.value)
        return self.reward[move]
        
    # Rules
    def stacking_color_rule(self, new_card, current_card):
        # print("Check stacking", current_card.suit.color, new_card.suit.color)
        return current_card.suit.color != new_card.suit.color
        
    def flipped_up_cards(self, card):
        return card.flipped
            
    def stacking_number_rule(self, new_cards, current_card):
        next_index = self.values.index(new_cards.value)+1
        # if next_index < 13:
        #     print("Current Card", str(new_cards), " Next possible card: ", self.values[next_index])
        #     print("Match? ", current_card.value != "K" and next_index < 13 and current_card.value == self.values[next_index])
        return current_card.value != "K" and next_index < 13 and current_card.value == self.values[next_index]
    
    def same_suit(self, new_card, current_card):
        return new_card.suit.suit_name == current_card.suit.suit_name
        
    def foundations_rule(self, location, new_card):
        # print("foundation")
        if len(self.state[location].cards) == 0 and new_card.value != "A":
            return False
        if len(self.state[location].cards) == 0 and new_card.value == "A":
            return True            
        current_card = self.state[location].cards[0]
        return self.stacking_number_rule(current_card, new_card) \
            and self.same_suit(new_card, current_card)
    
    def empty_piles_rule(self, new_card):
        return new_card.value == "K"
        
    def check_card_order(self, higherCard, lowerCard):
        # print("Trying to stack", lowerCard.value, " on ", higherCard.value)
        suits_different = self.suits[higherCard.suit] != self.suits[lowerCard.suit]
        value_consecutive = self.values[self.values.index(higherCard.value)-1] == lowerCard.value
        return suits_different and value_consecutive
    
    def check_if_completed(self):
        self.count+=1
        for val in range(0, 9, 1):
            if len(self.state[val].cards) != 0:
                return False
        return True
            
    def can_move_to_foundation(self, card):
        if card is None:
            return False
        elif len(self.state.foundations[card.suit].cards)>0:
            highest_value = self.state.foundations[card.suit].cards[0].value
            if self.values[self.values.index(highest_value)+1] == card.value:
                return True
            else:
                return False   
        else: 
            if card.value=="A":
                return True
            else:
                return False     
                
    def get_playable_count(self, location):
        if location < 6 \
            and len(self.state[location].cards) > 0:
            return 1
        return len(self.state[location].get_flipped_cards())
            
    def deterministic_actions(self):
        flipped_up_cards = []
        empty_pile = []
        
        # Get all cards that are face up or need to be flipped
        for i in range(len(self.play_piles)):
            pile = self.play_piles[i]
            # Check if pile has cards
            if len(pile.cards) == 0:
                empty_pile.append(i)
                continue
            if not pile.cards[0].flipped:
                self.possible_moves.append({"move": "flip", "location": i, "to": i})
            else:
                flipped_up_cards.append({"location": "pile", "start": i, "card": pile.card[0]})    
        
        # Get all foundation top cards
        for found in self.foundations:
            flipped_up_cards.append({"location": "foundation", "start": found.cards[0].suit.suit_name, "card": found.cards[0]})
                
        # Deck check
        if len(self.deck.cards) > 0:
            self.possible_moves.append({"move":"deck_draw"})
        else: 
            self.possible_moves.append({"move":"deck_reset"})
        
        # Add top discard card to flipped_up cards 
        if len(self.deck.discard) > 0:
            flipped_up_cards.append({"location": "discard", "start": "discard", "card": self.deck.discard[0]})
            
        # For all flipped up cards check what moves are available
        for card in flipped_up_cards:
            # Check for Kings and empty piles
            for pil in empty_pile:
                if self.empty_piles_rule(card.card):
                    self.possible_moves.append({"move": "pile_pile", "location": card.start, "to": pil})
                
            # Moveable to Foundation
            if self.foundations_rule(card.card):
                self.possible_moves.append({"move": card.location+"_foundation", "location": card.start, "to": self.foundations[card.suit.suit_name]})
                
            # Stacking cards
            for card2 in flipped_up_cards:
                if self.stacking_color_rule(card.card, card2.card) and \
                    self.stacking_number_rule(card.card, card2.card) and \
                    self.valid_move_rule(card.location+"_"+card2.location):
                    self.possible_moves.append({"move": card.location+"_"+card2.location, "location": card.start, "to": card2.start})
        
        # Check again for any flipped up card to move multiple cards
        