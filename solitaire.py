from card_elements import Card, Deck, Pile, Suit
import numpy as np

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
            9       Foundation 1 - Spade
            10      Foundation 2 - Heart
            11      Foundation 3 - Club
            12      Foundation 4 - Diamond
          
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
            "flip": .1,
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
        self.action_space = 8
        self.observation_space = 12
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
            "flip": .1,
            "foundation_pile": .01,
            "deck_reset": .01,
            "deck_draw": .1,
            "pile_pile": .1
        }
        
    def reset(self):
        # Initial state
        deck = Deck(self.values,self.suits)
        for i in range(7):
            thisPile = Pile()
            [thisPile.add_card(deck.deal_card()) for j in range(i+1)]
            thisPile.flip_first_card()  
            self.state.append(thisPile)
        self.state.append(deck)
        self.state.append(Pile())
        for suit in self.suits:
            self.state.append({suit.suit_name: Pile()})

    def step(self, action):        
        if self.check_if_completed():
            print("You won!")
            reward = 1
            done = True
            return np.array(self.state), reward, done, {}
        else:
            done = False

        if not self.valid_action(action):       
            return np.array(self.state), -1, done, {}
            
        reward, move = self.assign_reward(action)
        self.move_cards(action, move)
        
        return np.array(self.state), reward, done, {}
      
    def get_game_elements(self):
        return_object = {
            "deck": str(self.state[7]),
            "discard": str(self.state[8]),
            "play_piles": [str(self.state[pile]) for pile in range(0, 7)],
            "foundations": [str(suit) for suit in self.state[9:]]
        }
        return return_object
        
    def valid_action(self, action):
        
        next_top_card = self.state[action['next_location']].cards[0]
        print("Action:",action)
        
        # Cannot move cards that don't exist
        if action['number'] > len(self.state[action['current_location']].cards):
            print("Cannot move cards that don't exist")
            return False
        
        # Invalid discard, deck rules
        if action['next_location'] == 7:
            if len(self.state[action['next_location']].cards) != 0 or action['current_location'] != 8:
                print("Invalid discard, deck rules")
                return False
            if len(self.state[action['current_location']].cards) == 0:
                print("Invalid discard, deck rules")
                return False
        
        # Cannot flip flipped up cards
        if action['current_location'] == action['next_location'] and \
            action['number'] == 1 and \
            self.state[action['current_location']].cards[0].flipped:
            print("Cannot flip flipped up cards")
            return False
        
        # Cannot stack onto face down cards
        if not self.flipped_up_cards(next_top_card):
            print("Cannot stack onto face down cards")
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
            top_card = self.state[action['next_location']].cards[0]
            return self.foundations_rule(top_card)
        else:
            # Non-foundation moves
            top_card = self.state[action['next_location']].cards[0]
            bottom_card = self.state[action['current_location']].cards[-1]
            # Cannot stack onto blank spaces unless kings
            if len(self.state[action['next_location']].cards) == 0: 
                if not self.empty_piles_rule(bottom_card):
                    return False
            
            # Cannot stack on same colors
            if not self.stacking_color_rule(bottom_card, top_card):
                return False
            
            # Cannot stack out of order
            if not self.stacking_number_rule(bottom_card, top_card):
                return False
                
        return True
           
    def assign_reward(self, action):
        
        if action['current_location'] == action['next_location']:
            return self.reward['flip'], "flip"
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
        reward = self.reward[act]
        print(reward)
        return reward, act
        
    def move_cards(self, action, move):
        if move == "pile_pile":
            temp = []
            for card in range(0, action['number']):
                temp.append(self.state[action['current_location']].remove_card())
            for card in range(action['number'] - 1, -1, -1):
                self.state[action['next_location']].add_card(temp[card])
                print("Moving card", str(temp[card].suit), temp[card].value," from ", action['current_location'], " to ", action['next_location'])
        
        elif move == "flip":
            self.state[action['current_location']].cards[0].flip()
            card = self.state[action['current_location']].cards[0]
            print("Flipping card" + card.suit + card.value)
            
        elif move == "deck_discard":
            temp = self.state[action['current_location']].draw_top_card()
            self.state[action['next_location']].add_card(temp)
            print("Moving card" + temp.suit + temp.value +" from Deck to " + action['next_location'])

        elif move == "discard_deck":
            self.state[action['next_location']].cards = self.state[action['current_location']].cards[::-1].flip()
            self.state[action['current_location']] = []

        else:
            temp = self.state[action['current_location']].remove_card()
            self.state[action['next_location']].add_card(temp)
            print("Moving card" + temp.suit + temp.value +" from " + action['current_location'] + " to " + action['next_location'])
        
    # Rules
    def stacking_color_rule(self, new_card, current_card):
        return current_card.suit.color != new_card.suit.color
        
    def flipped_up_cards(self, card):
        return card.flipped
            
    def stacking_number_rule(self, new_cards, current_card):
        return current_card.value != "K" and current_card.value == self.values[self.values.index(new_cards.value)+1]
    
    def same_suit(self, new_card, current_card):
        return new_card.suit.suit_name == current_card.suit.suit_name
        
    def foundations_rule(self, new_card):
        if len(self.state.foundations[new_card.suit.suit_name].cards) == 0 and new_card.value == "A":
            return True
        current_card = self.state.foundations[new_card.suit.suit_name].cards[0]
        return self.stacking_number_rule(current_card, new_card) \
            and self.same_suit(new_card, current_card)
    
    def empty_piles_rule(self, new_card):
        return new_card.value == "K"
        
    def check_card_order(self, higherCard, lowerCard):
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
        