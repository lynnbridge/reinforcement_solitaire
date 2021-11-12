import random

class Card:
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.flipped = False
        
    def flip(self):
        self.flipped = not self.flipped
        
    def __str__(self):        
        return "{0} {1}".format(self.value,self.suit)
    
class Pile:
    
    def __init__(self):
        self.cards = []
        
    def add_card(self, Card):
        self.cards.insert(0,Card)
        
    def flip_first_card(self):
        if len(self.cards)>0:
            self.cards[0].flip()
            
    def get_flipped_cards(self):
        return [card for card in self.cards if card.flipped]
    
    def __str__(self):        
        returned_cards = [str(card) for card in reversed(self.get_flipped_cards())]
        flipped_down_count = len(self.cards) - len(self.get_flipped_cards())
        if flipped_down_count>0:
            returned_cards.insert(0,"{0} cards flipped down".format(flipped_down_count))
        return ", ".join(returned_cards)
        
    def cheat_move(self, current_card):
        # This will find the next smallest card from the pile 
        # place it in the foundations.
        print("pile check")
        
        

class Deck: 
    
    def __init__(self, values, suits):
        self.cards = []
        self.facedown = []
        self.cache = []
        self.populate(values,suits)
        self.shuffle()
        
    def __str__(self):
        return ", ".join([str(card) for card in self.cards])

    def populate(self, values, suits):
        for suit in suits:
            for value in values:
                thisCard = Card(suit,value)
                self.facedown.append(thisCard)  
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def get_first_card(self):
        if len(self.cards)>0:
            return self.cards[0]
        else:
            return None
    
    def take_first_card(self, flip=True):
        if len(self.cards)>0:
            next_card = self.cards.pop(0)
            if flip and len(self.cards)>0:
                self.cards[0].flip()
            return next_card
        else:
            return None
        
    def draw_card(self):
        if len(self.facedown) > 0:
            self.facedown[0].flip()
            self.cards.append(self.facedown.pop(0))
    
    def reset_deck(self):
        if len(self.facedown) == 0:
            self.facedown = self.cards[::-1].flip()
            self.cards = []
            
    def cheat_move(self):
        # This will take the next smallest card from the deck 
        # place it in the foundations.
        print("Nothing")