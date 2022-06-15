from afinn import Afinn

class Scorer(Afinn):
    pass

if __name__=="__main__":
    s = Scorer()
    print(s.score('This is utterly excellent!'))