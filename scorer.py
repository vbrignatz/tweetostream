from afinn import Afinn

class Scorer(Afinn):
    pass

if __name__=="__main__":
    s = Scorer()
    print(s.score('This is utterly excellent!'))

#creation d une methode qui reccupere le tweet et effectue une notaiton
def getscore(tweet: str) -> float:
    s = Scorer()
    return s.score(tweet)