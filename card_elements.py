import random

class Suit:
    def __init__(self, suit_code, color, suit_name):
        self.suit_code = suit_code
        self.color = color
        self.suit_name = suit_name
        
    def __str__(self):
        return "{0}".format(self.suit_code, self.color, self.suit_name)

class Card:
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.flipped = False
        
    def flip(self):
        self.flipped = not self.flipped
        
    def __str__(self):        
        return "{0} {1}".format(self.value,self.suit.suit_code)
    
class Pile:
    
    def __init__(self):
        self.cards = []
        
    def add_card(self, Card):
        self.cards.insert(0,Card)
        
    def remove_card(self):
        # Do I need to find the card?
        return self.cards.pop(0)        
        
    def flip_first_card(self):
        if len(self.cards)>0:
            self.cards[0].flip()
            
    def get_flipped_cards(self):
        return [card for card in self.cards if card.flipped]
    
    def __str__(self):       
        returned_cards = [str(card) for card in reversed(self.get_flipped_cards())]
        flipped_down_count = len(self.cards) - len(self.get_flipped_cards())
        if flipped_down_count>0:
            returned_cards.insert(0,"{0} card".format(flipped_down_count))
        return ", ".join(returned_cards)
        
    def cheat_move(self, current_card):
        # This will find the next smallest card from the pile 
        # place it in the foundations.
        print("pile check")     

class Deck: 
    
    def __init__(self, values, suits):
        self.cards = []
        self.cache = []
        self.populate(values,suits)
        self.shuffle()
        
    def __str__(self):
        return ", ".join([str(card) for card in self.cards])

    def populate(self, values, suits):
        for suit in suits:
            for value in values:
                thisCard = Card(suit,value)
                self.cards.append(thisCard)  
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal_card(self):
        if len(self.cards) > 0:
            return self.cards.pop(0)
    
    def draw_top_card(self):
        if len(self.cards) > 0:
            return self.cards.pop(0).flip()
        else:
            return None
        
    # def draw_card(self):
    #     if len(self.cards) > 0:
    #         self.cards[0].flip()
    #         self.cards.append(self.cards.pop(0))            
    
    def reset_deck(self):
        if len(self.cards) == 0:
            self.cards = self.discard[::-1].flip()
            self.discard = []
            
    def cheat_move(self):
        # This will take the next smallest card from the deck 
        # place it in the foundations.
        print("Nothing")