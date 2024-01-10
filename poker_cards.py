# -*- coding: utf-8 -*-
# Python 3

class Card:
    def __init__(self, id: int):
        self.id = id
        self.suit_code = id // 13
        self.rank = id % 13 + 1

    def __repr__(self):
        return ["S", "H", "D", "C"][self.suit_code] + ([None, "A"] + [str(i + 2) for i in range(9)] + ["J", "Q", "K"])[self.rank]


class Deck:
    def __init__(self):
        self.cards = [Card(i) for i in range(52)]

    def shuffle(self):
        import random
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()


class Hands:
    def __init__(self, cards: list):
        self.cards = cards
        self.ranks = [card.rank for card in self.cards]
        self.sort()
        self.hand = self.determine_hand()

    def __repr__(self):
        return str(self.cards)

    def sort(self):
        self.cards.sort(key=lambda x: x.suit_code)
        self.val = [[i, self.ranks.count(i)] for i in list(set(self.ranks))]
        self.val.sort(key=lambda x: x[0], reverse=True)
        self.val.sort(key=lambda x: x[0] == 1, reverse=True)
        self.val.sort(key=lambda x: x[1], reverse=True)
        for i in self.val:
            self.cards.sort(key=lambda x: x.rank == i[0])
            self.ranks.sort(key=lambda x: x == i[0])

    def determine_hand(self):
        if self.is_straight() and self.is_flush() and self.cards[0].rank == 1:
            return "9 Royal Straight Flush"
        elif self.is_flush() and self.is_straight():
            return "8 Straight Flush"
        elif self.val[0][1] == 4:
            return "7 Four of a Kind"
        elif self.val[0][1] == 3 and self.val[1][1] == 2:
            return "6 Full House"
        elif self.is_flush():
            return "5 Flush"
        elif self.is_straight():
            return "4 Straight"
        elif self.val[0][1] == 3:
            return "3 Three of a Kind"
        elif self.val[0][1] == 2 and self.val[1][1] == 2:
            return "2 Two Pair"
        elif self.val[0][1] == 2:
            return "1 One Pair"
        else:
            return "0 No Pair"

    def is_flush(self):
        return len(set([card.suit_code for card in self.cards])) == 1

    def is_straight(self):
        ranks = sorted(self.ranks.copy())
        return ranks == list(range(ranks[0], (ranks[0] + 5))) or ranks == [1, 10, 11, 12, 13]

def main():
    deck = Deck()
    deck.shuffle()
    hand = Hands([deck.draw() for _ in range(5)])
    print(hand.hand, hand)

if __name__ == '__main__':
    main()
