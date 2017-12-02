# Nick Porter, u0927946

import sys
import math

default_value = 0.0001
pos_tags = ['noun', 'verb', 'inf', 'prep']
phi = 'phi'


def log2(x):
    return math.log(x, 2)


def parseProbs(file_path):
    emission_probs = {}
    transition_probs = {}

    for line in open(file_path):
        tokens = line.lower().split()
        key = (tokens[0], tokens[1])

        if (key[0] in pos_tags and key[1] in pos_tags) or (key[0] == phi and key[1] in pos_tags) or (key[0] in pos_tags and key[1] == phi):
            transition_probs[key] = float(tokens[2])
        else:
            emission_probs[key] = float(tokens[2])

    return (emission_probs, transition_probs)


def parseSentences(file_path):
    arr = []
    for line in open(file_path):
        arr.append(line.lower())
    return arr


def emissionProbablity(emission_probs, w, t):
    if (w, t) not in emission_probs:
        return default_value
    return emission_probs[(w, t)]


def transitionProbablity(transition_probs, t1, t2):
    if (t1, t2) not in transition_probs:
        return default_value
    return transition_probs[(t1, t2)]


def viterbi(sentence, emission_probs, transition_probs):
    T = len(pos_tags)
    W = len(sentence.split())
    tokens = sentence.lower().split()

    scores = {}
    back_ptr = {}

    # Initialization Step
    for tag in pos_tags:
        first_word = tokens[0]
        x = emissionProbablity(emission_probs, first_word, tag)
        y = transitionProbablity(transition_probs, tag, phi)
        if x == 0.0 or y == 0.0:
            scores[(tag, 0)] = 'undefined'
        else:
            scores[(tag, 0)] = log2(x) + log2(y)
        back_ptr[(tag, 0)] = 0

    # Iteration Step
    for i in range(1, len(tokens)):
        word = tokens[i]
        for tag in pos_tags:
            maxValue = float('-inf')
            maxTag = None
            prev_word = tokens[i - 1]

            for other_tag in pos_tags:
                e = scores[(other_tag, i - 1)]
                if e == 'undefined':
                    continue
                t = transitionProbablity(transition_probs, tag, other_tag)
                tlog = log2(t)
                value = e + tlog

                if value > maxValue:
                    maxValue = value
                    maxTag = other_tag

            tran = emissionProbablity(emission_probs, word, tag)
            if tran == 0.0:
                scores[(tag, i)] = 'undefined'
            else:
                scores[(tag, i)] = log2(tran) + maxValue
            back_ptr[(tag, i)] = maxTag


    # Sequence Identification
    maxValue = float("-inf")
    last_word = tokens[-1]

    seq = []
    for tag in pos_tags:
        score = scores[(tag, len(tokens) - 1)]
        if score > maxValue:
            maxValue = score
            seq = [last_word + ' ' + tag]

    for i in reversed(range(0, len(tokens) - 1)):
        prev_word = tokens[i + 1]
        current_word = tokens[i]
        # Fix the zeros to nouns
        tupl = current_word + ' ' + back_ptr[(seq[-1].split()[1], i + 1)]
        seq.append(tupl)

    return scores, back_ptr, seq


def main():
    args = sys.argv
    emission_probs, transition_probs = parseProbs(args[1])
    sentences = parseSentences(args[2])

    for sentence in sentences:
        scores, back_ptr, seq = viterbi(sentence, emission_probs, transition_probs)

        print 'PROCESSING SENTENCE: %s' % sentence
        print 'FINAL VITERBI NETWORK'
        tokens = sentence.lower().split()
        for i in range(0, len(tokens)):
            for tag in pos_tags:
                print 'P(%s=%s) = %.4f' % (sentence.split()[i], tag, scores[(tag, i)])

        print '\nFINAL BACKPTR NETWORK'
        tokens = sentence.lower().split()
        for i in range(1, len(tokens)):
            word = tokens[i]
            for tag in pos_tags:
                print 'Backptr(%s=%s) = %s' % (word, tag, back_ptr[(tag, i)])

        key = seq[0].split()
        print '\nBEST TAG SEQUENCE HAS LOG PROBABILITY = %.4f' % scores[(key[1], len(tokens) - 1)]

        for line in seq:
            tokens = line.split()
            print '%s -> %s' % (tokens[0], tokens[1])

        print ''

main()