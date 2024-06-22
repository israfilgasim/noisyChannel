import math
from collections import Counter, defaultdict
import decimal

context = decimal.getcontext()
context.prec = 100


def distance(base_word, target_word):

    l1 = len(base_word)
    l2 = len(target_word)

    matrix = [[float('inf')] * (l2 + 1) for i in range(l1 + 1)]


    for i in range(l1 + 1):
        for j in range(l2 + 1):
            if i == 0:
                matrix[i][j] = j
            elif j == 0:
                matrix[i][j] = i
            else:
                change = 0 if base_word[i-1] == target_word[j-1] else 1
                transposition = float('inf')
                if i > 1 and j > 1 and base_word[i-1] == target_word[j-2] and base_word[i-2] == target_word[j-1]:
                    transposition = matrix[i-2][j-2] + 1
                matrix[i][j] = min(matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + change, transposition)
    
    return matrix[l1][l2]


class Weight:

    def __init__(self):
        self.unigram = Counter()
        self.bigram = defaultdict(Counter)
        self.trigram = defaultdict(Counter)
        self.allWords = 0

    
    def train(self, corpus):
        ccccc = 0
        for sentence in corpus:
            ccccc += 1
            if ccccc % 100000 == 0:
                print(str(ccccc) + ' sentences processed')
            self.allWords += len(sentence)
            self.unigram.update(sentence)

            bigram = ['<s>'] + sentence + ['</s>']
            trigram = ['<s>'] + bigram

            for i in range(len(bigram) - 1):
                history = tuple(bigram[i:i+1])
                nextW = bigram[i + 1]

                self.bigram[history][nextW] += 1

            for i in range(len(trigram) - 2):
                history = tuple(trigram[i:i+2])
                nextW = trigram[i + 2]

                self.trigram[history][nextW] += 1
            
    def probability(self, history, nextW):
        prob = 0
        history = tuple(history)
        if len(history) == 2:
            if nextW in self.trigram[history]:
                prob = decimal.Decimal(self.trigram[history][nextW]) / decimal.Decimal(sum(self.trigram[history].values()))
                return prob
            history = history[1:]
        if len(history) == 1:
            if nextW in self.bigram[history]:
                prob = decimal.Decimal(self.bigram[history][nextW]) / decimal.Decimal(sum(self.bigram[history].values()))
                return prob
        else:
            prob = decimal.Decimal(self.unigram[nextW]) / decimal.Decimal(self.allWords)
            return prob
        return prob
    

    def correct_input(self, input_text):
        if " " not in input_text:
            suggestions = []
            minDis = float('inf')
            for word in self.unigram:
                if len(word) - len(input_text) > 2 or word == input_text:
                    continue
                levDis = distance(input_text, word)
                if levDis < minDis:
                    suggestions = []
                    suggestions.append(word)
                    minDis = levDis
                elif levDis == minDis:
                    suggestions.append(word)
            if self.unigram[input_text] > 0:
                suggestions.append(input_text)
            first = [0, '']
            second = [0, '']
            third = [0, '']
            for word in suggestions:
                prob = self.unigram[word]
                if prob > first[0]:
                    third = second
                    second = first
                    first = [prob, word]
                elif prob > second[0]:
                    third = second
                    second = [prob, word]
                elif prob > third[0]:
                    third = [prob, word]
            return [first[1], second[1], third[1]]
        else:
            words = input_text.split()
            token = ['<s>'] * 2 + words + ['</s>']
            corrected = []
            for i in range(2, len(token) - 1):
                prob = 0
                nextW = ''
                history = token[i-2:i]
                nextwords = self.correct_input(token[i])
                for nextword in nextwords:
                    probW = self.probability(history, nextword)
                    if probW > prob:
                        prob = probW
                        nextW = nextword
                if nextW == '':
                    nextW = self.correct_input(token[i])[0]
                corrected.append(nextW)
            return corrected



        
    def parser(self, input_text):
        suggestions = []
        maxProb = 0
        l = len(input_text)
        for i in range(1,l):
            first = input_text[:i]
            second = input_text[i:]
            first_sugg = self.correct_input(first)[0]
            second_sugg = self.correct_input(second)[0]
            suggestions.append([first_sugg, second_sugg])
            # for f in first_sugg:
            #     for s in second_sugg:
            #         prob = self.bigram[(f,)][s]
            #         if prob > maxProb:
            #             suggestions = [f,s]
            #             maxProb = prob
        return suggestions


                