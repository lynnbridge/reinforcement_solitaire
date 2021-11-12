from card_elements import Card, Deck, Pile

class Game:
    
    values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    
    suits = { #keys are unicode symbols for suits
        u'\u2660': "black",
        u'\u2665': "red",
        u'\u2663': "black",
        u'\u2666': "red",
    }
    
    scoring = {
        "d_p": 5, # deck to pile
        "d_f": 10, # deck to foundation
        "p_f": 10, # pile to foundation
        "pp": 5, # pile flip
        "f_p": -15, # foundation to pile
        "dd": -10, # deck flip over
        "": 0 # anything else
    }
    
    num_play_piles = 7
    
    def __init__(self):
        self.deck = Deck(self.values,self.suits)
        self.play_piles = []
        self.current_score = 0
        for i in range(self.num_play_piles):
            thisPile = Pile()
            [thisPile.add_card(self.deck.take_first_card(flip=False)) for j in range(i+1)]
            thisPile.flip_first_card()  
            self.play_piles.append(thisPile)
        self.foundations = {suit: Pile() for suit in self.suits}
        self.deck.cards[0].flip()
        
    def score_update(self, move):
        self.current_score += self.scoring[move]
    
    def get_game_elements(self):
        return_object = {
            "deck": str(self.deck),
            "play_piles": [str(pile) for pile in self.play_piles],
            "foundations": {suit: str(pile) for suit, pile in self.foundations.items()}
        }
        return return_object
        
    def check_card_order(self,higherCard,lowerCard):
        suits_different = self.suits[higherCard.suit] != self.suits[lowerCard.suit]
        value_consecutive = self.values[self.values.index(higherCard.value)-1] == lowerCard.value
        return suits_different and value_consecutive
    
    def check_if_completed(self):
        deck_empty = len(self.deck.cards)==0
        piles_empty = all(len(pile.cards)==0 for pile in self.play_piles)
        blocks_full = all(len(pile.cards)==13 for suit,pile in self.foundations.items())
        return deck_empty and piles_empty and blocks_full
            
    def add_to_block(self, card):
        if card is None:
            return False
        elif len(self.foundations[card.suit].cards)>0:
            highest_value = self.foundations[card.suit].cards[0].value
            if self.values[self.values.index(highest_value)+1] == card.value:
                self.foundations[card.suit].cards.insert(0,card)
                return True
            else:
                return False   
        else: 
            if card.value=="A":
                self.foundations[card.suit].cards.insert(0,card)
                return True
            else:
                return False
        
    def take_turn(self, verbose=False):
        #Pre: flip up unflipped pile end cards -> do this automatically
        [pile.cards[0].flip() for pile in self.play_piles if len(pile.cards)>0 and not pile.cards[0].flipped]

        #1: check if there are any play pile cards you can play to block piles
        for pile in self.play_piles:
            if len(pile.cards) > 0 and self.add_to_block(pile.cards[0]):
                card_added = pile.cards.pop(0)
                if verbose:
                    print("Adding play pile card to block: {0}".format(str(card_added)))
                return True

        #2: check if cards in deck can be added
        if self.add_to_block(self.deck.get_first_card()):
            card_added = self.deck.take_first_card()
            if verbose:
                print("Adding card from deck to block: {0}".format(str(card_added)))
            return True

        #3: move kings to open piles
        for pile in self.play_piles:
            if len(pile.cards)==0: #pile has no cards
                for pile2 in self.play_piles:
                    if len(pile2.cards)>1 and pile2.cards[0].value == "K":
                        card_added = pile2.cards.pop(0)
                        pile.add_card(card_added)
                        if verbose:
                            print("Moving {0} from Pile to Empty Pile".format(str(card_added)))
                        return True

                if self.deck.get_first_card() is not None and self.deck.get_first_card().value == "K":
                    card_added = self.deck.take_first_card()
                    pile.add_card(card_added)
                    if verbose:
                        print("Moving {0} from Deck to Empty Pile".format(str(card_added)))
                    return True

        #4: add drawn card to play_piles 
        for pile in self.play_piles:
            if len(pile.cards)>0 and self.deck.get_first_card() is not None:
                if self.check_card_order(pile.cards[0],self.deck.get_first_card()):
                    card_added = self.deck.take_first_card()
                    pile.add_card(card_added) 
                    if verbose:
                        print("Moving {0} from Deck to Pile".format(str(card_added)))
                    return True

        #5: move around cards in play_piles
        for pile1 in self.play_piles:
            pile1_flipped_cards = pile1.get_flipped_cards()
            if len(pile1_flipped_cards)>0:
                for pile2 in self.play_piles:
                    pile2_flipped_cards = pile2.get_flipped_cards()
                    if pile2 is not pile1 and len(pile2_flipped_cards)>0:
                        for transfer_cards_size in range(1,len(pile1_flipped_cards)+1):
                            cards_to_transfer = pile1_flipped_cards[:transfer_cards_size]
                            if self.check_card_order(pile2.cards[0],cards_to_transfer[-1]):
                                pile1_downcard_count = len(pile1.cards) - len(pile1_flipped_cards)
                                pile2_downcard_count = len(pile2.cards) - len(pile2_flipped_cards)
                                if pile2_downcard_count < pile1_downcard_count:
                                    [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                    pile1.cards = pile1.cards[transfer_cards_size:]
                                    if verbose:
                                        print("Moved {0} cards between piles: {1}".format(
                                            transfer_cards_size,
                                            ", ".join([str(card) for card in cards_to_transfer])
                                                                                         ))
                                    return True
                                elif pile1_downcard_count==0 and len(cards_to_transfer) == len(pile1.cards):
                                    [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                    pile1.cards = []
                                    if verbose:
                                        print("Moved {0} cards between piles: {1}".format(
                                            transfer_cards_size,
                                            ", ".join([str(card) for card in cards_to_transfer])
                                                                                         ))
                                    return True
        return False
        
    def act(self):
        [pile.cards[0].flip() for pile in self.play_piles if len(pile.cards)>0 and not pile.cards[0].flipped]
                    
    def simulate(self, draw = False, verbose=False):
        
        # clear cache if last turn was not card draw
        if not draw:
            self.deck.cache = []
        
        turnResult = self.take_turn(verbose=verbose)
        
        if turnResult:
            self.simulate(verbose=verbose)
                    
        else:
            #End: draw from deck
            if len(self.deck.cards)>0:

                currentCard = self.deck.cards[0]

                if currentCard in self.deck.cache:
                    if verbose:
                        print("No more moves left!")
                    return 

                else:
                    self.deck.draw_card()
                    if verbose:
                        print("Drawing new card: {0}".format(str(currentCard)))
                    self.deck.cache.append(currentCard)
                    return self.simulate(draw=True, verbose=verbose)
            else:
                if verbose:
                    print("No more moves left!")
                return