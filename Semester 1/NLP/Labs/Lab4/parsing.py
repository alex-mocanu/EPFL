import sys
import nltk
from nltk.tree import *
from nltk.draw import tree
from nltk.grammar import Nonterminal


def run_task(task_to_run):
    if task_to_run == 1:
        task1()
    elif task_to_run == 2:
        task2()
    elif task_to_run == 3:
        task3()
    else:
        task4()


def display_trees(parser, tokens):
    trees = parser.parse(tokens)
    for tree in trees:
        print(tree)
        tree.draw()


def task1():
    sentence1 = 'I saw an elephant'
    sentence2 = 'I saw an elephant in my pajamas'
    grammar = '''
        S   -> NP VP     [1.0]
        PP  -> P NP      [1.0]
        NP  -> Det N     [0.4]
        NP  -> Det N PP  [0.2]
        VP  -> V NP      [0.5]
        VP  -> VP PP     [0.5]
        NP  -> 'I'        [0.4]
        Det -> 'an'       [0.5]
        Det -> 'my'       [0.5]
        N   -> 'elephant' [0.5]
        N   -> 'pajamas'  [0.5]
        V   -> 'saw'      [1.0]
        P   -> 'in'       [1.0]
        '''

    # Define the grammar
    g = nltk.PCFG.fromstring(grammar)

    # Tokenize each sentence
    tokens1 = nltk.word_tokenize(sentence1)
    tokens2 = nltk.word_tokenize(sentence2)

    # Parse using the chart parser
    chart_parser = nltk.ChartParser(g)
    print("Chart parser trees")
    display_trees(chart_parser, tokens1)
    display_trees(chart_parser, tokens2)

    # Parse using viterbi parser
    viterbi_parser = nltk.ViterbiParser(g)
    print("Viterbi trees")
    display_trees(viterbi_parser, tokens1)
    display_trees(viterbi_parser, tokens2)


def task2():
    sentence1 = 'Alice wondered with Bob in the empty city streets'
    sentence2 = 'Bob offered Alice an iguana for her birthday'
    sentence3 = 'Alice gave an inspiring speech at the conference on education'
    grammar = '''
        S       -> NP VP
        PNP     -> Prep NP
        VP      -> V | VP NP | VP PNP
        NP      -> N | N NP | Adj NP | Det NP
        V       -> 'wondered' | 'offered' | 'gave'
        NP      -> 'Alice' | 'Bob'
        N       -> 'city' | 'streets' | 'iguana' | 'birthday' | 'speech' | 'conference' | 'education'
        Adj     -> 'empty' | 'inspiring'
        Det     -> 'the' | 'an' | 'her'
        Prep    -> 'with' | 'in' | 'for' | 'at' | 'on'
    '''

    # Define the grammar
    g = nltk.CFG.fromstring(grammar)

    # Tokenize each sentence
    tokens1 = nltk.word_tokenize(sentence1)
    tokens2 = nltk.word_tokenize(sentence2)
    tokens3 = nltk.word_tokenize(sentence3)

    # Parse using the chart parser
    chart_parser = nltk.ChartParser(g)
    display_trees(chart_parser, tokens1)
    display_trees(chart_parser, tokens2)
    display_trees(chart_parser, tokens3)


def task3():
    treebank = nltk.corpus.treebank
    dataset_size = len(treebank.parsed_sents())

    # Split the dataset in train and test
    split_size = int(dataset_size * 0.97)
    learning_set = treebank.parsed_sents()[:split_size]
    test_set = treebank.parsed_sents()[split_size:]

    # Create a set containing the raw sentences
    sents = treebank.sents()
    raw_test_set = [[w for w in sents[i]] for i in range(split_size, dataset_size)]

    # Start extracting the production rules
    tbank_productions = []

    # For all of the (parsed) sentences in the learning set, extract the
    # productions
    for sent in learning_set:
        for production in sent.productions():
            tbank_productions.append(production)

    # Now, we will add the lexical rules for the ENTIRE lexicon.
    for word, tag in treebank.tagged_words():
        t = Tree.fromstring("(" + tag + " " + word + ")")
        for production in t.productions():
            tbank_productions.append(production)

    # At this point, we have the syntactic rules extracted from the
    # learning set and all of the lexical rules. We are ready to extract
    # the PCFG.
    tbank_grammar = nltk.grammar.induce_pcfg(Nonterminal('S'), tbank_productions)

    print("Test the grammar")
    parser = nltk.ViterbiParser(tbank_grammar)
    n_sents = len(raw_test_set)
    correct_sents = 0
    for i, sent in enumerate(raw_test_set):
        trees = parser.parse(sent)
        print(test_set[i], list(trees))
        if test_set[i] in trees:
            correct_sents += 1

    print(f'{100 * correct_sents / n_sents}% of the sentences were correctly tagged')


if __name__ == '__main__':
    task_to_run = int(sys.argv[1])

    run_task(task_to_run)
