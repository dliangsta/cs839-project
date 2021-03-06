import pickle
import json
import string
import numpy as np
from instance import *
from location import *

class Vectorizer:
    def __init__(self, prune_list=None, cryptocurrencies=None):
        self.one_count = 0
        self.zero_count = 0
        self.prune_list = prune_list
        self.cryptocurrencies = [cryptocurrency.lower() for cryptocurrency in cryptocurrencies]
        self.instances = []

    def vectorize(self, docs):
        for i in docs:
            with open('data/labeled/' + str(i), encoding='utf8') as f:
                data = [line.strip() for line in f.readlines()]

                # Iterate over lines in document.
                for j, labeled_line in enumerate(data):
                    original_line = data[j-1]

                    # Skip every other line, because we handle the lines in pairs.
                    if j % 2 == 1: 
                        self.vectorize_line(i, j, original_line, labeled_line)
        return self.instances

    def vectorize_line(self, i, j, original_line, labeled_line):
        # Iterate over each character in the line to find each word.
        num_words = [1, 2]
        for num_word in num_words:
            k = 0
            done = False
            while k < len(labeled_line):
                # Index of end of word.
                l = k
                for n in range(num_word):
                    l = original_line.find(' ', l) # keep finding next space depending on how many words we are looking for

                # If cannot be found, l will be -1 so we are at the end of the line.
                if l < k:
                    word = original_line[k:] # grab rest of line
                    done = True
                else:
                    word = original_line[k:l]

                ll = labeled_line.find(' ', k) # find next space in labeled line from start of word
                # if there is no space in the labeled segment where there is in the original line, we shouldn't classify this chunk of a 2-part word
                label = 1 if labeled_line[k] != '`' and l == ll else 0

                # Find next word
                k_n = l+1
                if k_n < len(original_line):
                    l_n = original_line.find(' ', k_n)
                    next_word = '' if l_n < k_n else original_line[k_n:l_n]

                if len(word) and any([c.isalpha() for c in word]):
                    if not self.shouldPruneWord(word):
                        # Make features.
                        feature_functions = [self.hasAllCaps,
                                            self.isSurroundedByParentheses,
                                            self.wordLength,
                                            self.numCapitals,
                                            self.firstLetterCapitalized,
                                            self.containsCashSubstring,
                                            self.containsCoinSubstring,
                                            self.containsTokenSubstring,
                                            self.containsForwardSlash,
                                            self.containsDash,
                                            self.containsApostrophe,
                                            self.containsDot,
                                            self.containsComma,
                                            self.containsMoneySign,
                                            self.containsPound,
                                            self.containsPlus,
                                            self.containsIumSubstring,
                                            self.containsEumSubstring,
                                            #self.inCryptocurrenciesList
                                            ] 
                        features = [func(word) for func in feature_functions] + self.charCounts(word) + self.alphabetCounts(next_word)

                        location = Location(i, j, k, l)
                        instance = Instance(location=location, 
                                            label=label, 
                                            word=word,
                                            features=features)

                        self.instances.append(instance)
                        if label == 1:
                            self.one_count += 1
                        else:
                            self.zero_count += 1
                if not done:
                    k = l+1
                else:
                    break

    def shouldPruneWord(self, word):
        word = removePunctuation(word)
        return word in self.prune_list

    # Features
    def hasAllCaps(self, word):
        word = removePunctuation(word)
        return int(word.upper() == word)

    def isSurroundedByParentheses(self, word):
        word = removePunctuation(word)
        return int(word[0] == '(' and word[-1] == ')')

    def inCryptocurrenciesList(self, word):
        word = removePunctuation(word)
        return int(word.lower() in self.cryptocurrencies)

    def wordLength(self, word):
        word = removePunctuation(word)
        return len(word)

    def numCapitals(self, word):
        word = removePunctuation(word)
        return sum(1 for c in word if c.isupper() and c.isalpha())

    def firstLetterCapitalized(self, word):
        word = removePunctuation(word)
        return int(word[0].isupper())

    def containsCashSubstring(self, word):
        return int('cash' in word.lower())

    def containsCoinSubstring(self, word):
        return int('coin' in word.lower())

    def containsTokenSubstring(self, word):
        return int ('token' in word.lower())

    def containsEumSubstring(self, word):
        return int('eum' in word.lower())

    def containsIumSubstring(self, word):
        return int('ium' in word.lower())

    def containsForwardSlash(self, word):
        return int('/' in word)

    def containsDash(self, word):
        return int('-' in word)

    def containsApostrophe(self, word):
        return int('\'' in word)

    def containsDot(self, word):
        return int('.' in word)

    def containsComma(self, word):
        return int(',' in word)

    def containsMoneySign(self, word):
        return int('$' in word)

    def containsPound(self, word):
        return int('#' in word)

    def containsPlus(self, word):
        return int('+' in word)


    def charCounts(self, word):
        return [word.count(chr(letter)) for letter in range(128)]

    def alphabetCounts(self, word):
        lower = word.lower()
        return [lower.count(chr(letter)) for letter in range(97, 123)]



def main():
    # Iterate over all documents.

    with open('data/prune_list.json') as f:
        prune_list = json.load(f)
    with open('data/cryptocurrencies_list.json') as f:
        cryptocurrencies = json.load(f)

    docs = list(range(1, 301))

    v = Vectorizer(prune_list, cryptocurrencies)

    instances = v.vectorize(docs)
    # for instance in instances:
    #     print(instance)

    np.random.seed(0)
    np.random.shuffle(docs)
    I_size = int(len(docs) * (2.0/3))
    J_size = len(docs) - I_size
    I_docs = docs[:I_size]
    J_docs = docs[I_size:]


    I_instances = []
    J_instances = []

    for instance in instances:
        if instance.location.doc_num in I_docs:
            I_instances.append(instance)
        elif instance.location.doc_num in J_docs:
            J_instances.append(instance)

    print(len(docs), I_size, J_size, len(I_docs), len(J_docs), len(I_instances), len(J_instances))
    print(v.one_count, v.zero_count)

    # Save dataset.
    with open('data/I_instances.pkl','wb') as f:
        pickle.dump(I_instances, f)
    with open('data/J_instances.pkl','wb') as f:
    	pickle.dump(J_instances, f)
    with open('data/I_docs.json','w') as f:
        json.dump(I_docs, f)
    with open('data/J_docs.json','w') as f:
        json.dump(J_docs, f)

# Utilities
def removePunctuation(word):
    punctuation = ['\'','"','.','?','!',',',';',':','[',']']
    while len(word) and word[0] in punctuation:
        word = word[1:]
    while len(word) and word[-1] in punctuation:
        word = word[:-1]
    return word



if __name__ == '__main__':
    main()