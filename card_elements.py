import random
import tensorflow as tf

class Suit:
    def __init__(self, suit_code=None, color=0, suit_name=0, value=0):
        self.suit_code = suit_code
        self.color = color
        self.suit_name = suit_name
        self.value = value
        
    def get_color_number(self):
        if self.color == "red":
            return 1
        elif self.color == "black":
            return 2
        return 0
        
    def __str__(self):
        return "{0}".format(self.suit_code)

class Card:
    def __init__(self, suit=Suit(), value=0, empty=True):
        self.suit = suit
        self.value = value
        self.flipped = False
        self.empty = empty
        
    def flip(self):
        self.flipped = not self.flipped
        
    def __str__(self):        
        return "{0} {1}".format(self.value,self.suit.suit_code)
    
class Pile:
    def __init__(self):
        self.cards = []
        self.cache = []
        
    def insert_card(self, Card):
        self.cards.insert(0,Card)
        
    def remove_card(self):
        if len(self.cards) > 0:
            return self.cards.pop(0)     
        return None
        
    def flip_top_card(self):
        if len(self.cards)>0:
            self.cards[0].flip()
            
    def get_flipped_cards(self):
        return [card for card in self.cards if card.flipped]
        
    def populate(self, values, suits):
        for suit in suits:
            for value in values:
                thisCard = Card(suit,value,False)
                self.cards.append(thisCard)  
    
    def shuffle(self):
        random.shuffle(self.cards)
            
    def draw_top_card(self):
        if len(self.cards) > 0:
            return self.cards.pop(0).flip()
        else:
            return None
            
    def empty_pile(self):
        if len(self.cards) == 0:
            self.cards = self.discard[::-1].flip()
            self.discard = []
    
    def __str__(self):
        # return ", ".join([str(card) for card in self.cards])
        returned_cards = [str(card) for card in reversed(self.get_flipped_cards())]
        flipped_down_count = len(self.cards) - len(self.get_flipped_cards())
        if flipped_down_count>0:
            returned_cards.insert(0,"{0} card(s)".format(flipped_down_count))
        return ", ".join(returned_cards)
        
    def cheat_move(self, current_card):
        # This will find the next smallest card from the pile 
        # place it in the foundations.
        print("pile check")     