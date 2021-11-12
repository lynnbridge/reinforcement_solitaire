import pprint
pp = pprint.PrettyPrinter(indent=2)

from solitaire import Game

def main():
    thisGame = Game()
    pp.pprint(thisGame.get_game_elements())
    thisGame.simulate(verbose=True)
    print()
    pp.pprint(thisGame.get_game_elements())
    print()
    if(thisGame.check_if_completed()):
        print("Congrats! You won!")
    else:
        print("Sorry, you did not win")
    
    return
    
if __name__ == "__main__":
    main()