import codecs
from math import factorial
import os
import itertools
import copy
import operator
import random

#Function that check if the file format is CONLL

def check_format(path):
    result = ''
    ids = []
    heads = []
    f = codecs.open(path, 'r', 'utf-8-sig')
    for line in f:
        line = line.strip()
        parts = line.split()
        if len(parts) < 10 and len(parts) != 0:
            result = 'Incorrect format'
            continue
        if len(parts) != 0:
            if parts[0] == '1':
                ids = []
                heads = []
            ids.append(parts[0])
            heads.append(parts[-4])
    for h in heads:
        if h not in ids and h != '0':
            result = 'Incorrect format'
    for i in range(0, len(ids) - 1):
        if int(ids[i]) != int(ids[i + 1]) - 1:
            result = 'Incorrect format'
    if result == '':
        result = 'Correct format'
    return result

def check_file(path):
    if path.endswith('.conll') == False:
        print('\nFile format must be conll\n')
        exit()
    else:
        if check_format(path) == 'Incorrect format':
            print('\nIncorrect format\n')
            exit()
        else:
            print('\nFormat of the file: Confirmed\n')

# Class of a tree node

class tree_node:
    
    def __init__(self, id, word, head, path_to_root, punct):
        self.id = id
        self.word = word
        self.head = head
        self.path_to_root = path_to_root
        self.punct = punct

# Function that transorms the input CONLL file into a tree with the inclusion of punctuation

def make_tree(path):
    trees = []
    tree = []
    f = codecs.open(path, 'r', 'utf-8-sig')
    for line in f: 
        line = line.strip()
        parts = line.split()
        if len(parts) == 0:
            continue
        if parts[0] == '1' and len(tree) != 0:
            trees.append(tree)
            tree = []
        if parts[-5] == 'punct':
            tree_part = tree_node(int(parts[0]), parts[1], int(parts[-4]), [], 1)
        else:
            tree_part = tree_node(int(parts[0]), parts[1], int(parts[-4]), [], 0)
        tree.append(tree_part)
    f.close()
    for s in trees:
        for t in s:
            head = t.head
            path = [t.head]
            while head != 0:
                for r in s:
                    if head == r.id:
                        head = r.head
                        path.append(r.head)
            t.path_to_root = path
    return trees

# Function that transorms the input CONLL file into a tree without punctuation

def make_tree_wo_punctuation(path):
    trees = []
    tree = []
    f = codecs.open(path, 'r', 'utf-8-sig')
    p = 0
    all_new_ids = []
    new_ids = {}
    for line in f:
        line = line.strip()
        parts = line.split()
        if len(parts) == 0:
            continue
        if parts[0] == '1' and len(tree) != 0:
            trees.append(tree)
            tree = []
            p = 0
            all_new_ids.append(new_ids)
            new_ids = {}    
        if parts[-3] != 'punct':
            tree_part = tree_node(int(parts[0]) - p, parts[1], int(parts[-4]), [], 0)
            if p != 0:
                new_ids[int(parts[0])] = int(parts[0]) - p
            tree.append(tree_part)
        else:
            p += 1
    f.close()
    for s in range(len(trees)):
        for t in trees[s]:
            if t.head in all_new_ids[s]:
                t.head = all_new_ids[s][t.head]
    for s in trees:
        for t in s:
            head = t.head
            path = [t.head]
            while head != 0:
                for r in s:
                    if head == r.id:
                        head = r.head
                        path.append(r.head)
            t.path_to_root = path
    return trees

# ACCURACY - the procent of correctly identified heads.

def accuracy(parsed, gold):
    acc = []
    for i in range(len(parsed)):
        right = 0
        for l in range(len(parsed[i])):
            if parsed[i][l].head == gold[i][l].head:
                right += 1
        a = round(right/len(parsed[i]), 4)
        acc.append(a)
    return acc

# ROOT ACCURACY - 1 if the root is correctly identified, 0 if not

def root_accuracy(parsed, gold):
    root_accuracies = []
    for i in range(len(parsed)):
        root1 = 0
        root2 = 0
        for l in range(len(parsed[i])):
            if parsed[i][l].head == 0:
                root1 = parsed[i][l].id
            if gold[i][l].head == 0:
                root2 = gold[i][l].id
        if root1 == root2:
            root_accuracy = 1
        else:
            root_accuracy = 0
        root_accuracies.append(root_accuracy)
    return root_accuracies

# RELATIONS ACCURACY - the procent od correctly identified relations

def relations(parsed, gold):
    relations = []
    for p in range(len(parsed)):
        right = 0
        bonds = []
        for r in parsed[p]:
            bond1 = str(r.id) + ' - ' + str(r.head)
            bond2 = str(r.head) + ' - ' + str(r.id)
            bonds.append(bond1)
            bonds.append(bond2)
        for g in gold[p]:
            bond = str(g.id) + ' - ' + str(g.head)
            if bond in bonds:
                right += 1
        n = round(right / len(parsed[p]), 4)
        relations.append(n)
    return relations

# PATH EDIT DISTANCE - the number of operations it takes to transform all the paths of on tree to all the paths of the other tree.

def ped(parsed, gold):
    ped = []
    for i in range(len(parsed)):
        t = 0
        for l in range(len(parsed[i])):
            t += len([a for a in parsed[i][l].path_to_root+gold[i][l].path_to_root if (a not in parsed[i][l].path_to_root) or (a not in gold[i][l].path_to_root)])
        t = round(1 - (t / ((len(parsed[i]) - 1) * len(parsed[i]))), 4)
        ped.append(t)
    return ped

# NUMBER OF NODES - the total length of paths divided by maximum length of paths.

def count_nodes(tree):
    nodes = -1
    for t in tree:
        nodes += len(t.path_to_root)
    return nodes
    
def span_difference(parsed, gold):
    norm_diff = []
    for i in range(len(parsed)):
        nodes1 = count_nodes(parsed[i])
        nodes2 = count_nodes(gold[i])
        diff = abs(nodes1 - nodes2)
        max_id = parsed[i][-1].id
        max_diff = factorial(max_id) - (2 * max_id - 1)
        diff = 1 - round(diff / max_diff, 4)
        norm_diff.append(diff)
    return norm_diff

# PATH LENGTH

def path_length(parsed, gold):
    lengths = []
    for i in range(len(parsed)):
        tree_diff = []
        for l in range(len(parsed[i])):
            diff = abs(len(parsed[i][l].path_to_root) - len(gold[i][l].path_to_root))
            max_diff = len(parsed[i]) - 1
            tree_diff.append(round(diff / max_diff, 4))
        lengths.append(round(1 - round(sum(tree_diff)/len(tree_diff), 4), 4))
    return lengths
        
            

# NORMALIZATION - summing up all the metrics

def normalize(metric1, metric2, metric3, metric4, metric5):
    normalization = []
    for i in range(len(metric1)):
        norm = round(0.25 * metric1[i] + 0.1 * metric2[i] + 0.4 * metric3[i] + 0.2 * metric4[i] + 0.05 * metric5[i], 4)
        normalization.append(norm)
    return normalization

# Function to count how close an option for the generalized gold is to the two golds

def average_score(option, gold1, gold2):
    option = [option]
    gold1 = [gold1]
    gold2 = [gold2]
    metric11 = accuracy(option, gold1)
    metric21 = accuracy(option, gold2)
    metric12 = relations(option, gold1)
    metric22 = relations(option, gold2)
    metric13 = ped(option, gold1)
    metric23 = ped(option, gold2)
    metric14 = path_length(option, gold1)
    metric24 = path_length(option, gold2)
    metric15 = root_accuracy(option, gold1)
    metric25 = root_accuracy(option, gold2)
    norm1 = normalize(metric11, metric12, metric13, metric14, metric15)
    norm2 = normalize(metric21, metric22, metric23, metric24, metric25)
    avg_norm = (norm1[0] + norm2[0])/2
    return avg_norm

# Function to create a generalized gold tree

def generalize(gold1, gold2):
    generalized = []
    acc = accuracy(gold1, gold2)
    for i in range(len(gold1)):
        #print(i)
        if acc[i] == 1:
            generalized.append(gold1[i])
            continue
        wrong = []
        for g in range(len(gold1[i])):
            if gold1[i][g].head != gold2[i][g].head:
                wrong.append(gold1[i][g].id)
        options = itertools.product([1, 2], repeat=len(wrong))
        possibilities = []
        scores = []
        try:
            options = list(options)
            if len(options) > 20:
                options = random.sample(options, 20)
        except MemoryError:
            m = 0
        m = 0
        for o in options:
            if m > 20:
                break
            n = 0
            poss = copy.deepcopy(gold1[i])
            for g in range(len(gold1[i])):
                if gold1[i][g].head != gold2[i][g].head:
                    if o[n] == 1:
                        poss[g].head = gold1[i][g].head
                    if o[n] == 2:
                        poss[g].head = gold2[i][g].head
                    n += 1
            for p in poss:
                head = p.head
                path = [p.head]
                n = 0
                while head != 0 and n <= len(poss) + 1:
                    for o in poss:
                        if head == o.id:
                            head = o.head
                            path.append(o.head)
                            n += 1
                p.path_to_root = path
            possibilities.append(poss)
            scores.append(average_score(poss, gold1[i], gold2[i]))
            m += 1
        try:
            max_score = max(scores)
            max_score_index = [l for l, j in enumerate(scores) if j == max_score]
            gen = possibilities[max_score_index[0]]
        except ValueError:
            gen = gold1[i]
        generalized.append(gen)                                        
    return generalized

# Function to write the result in file

def write_result(name, gold, parsed, metric1, metric2, metric3, metric4, metric5, normalization):
    f = open(name, 'w')
    f.write('ID\t\tLength\t\tAccuracy\t\tRoot Score\t\tRelations\t\tPED\t\t\tSpan Difference\tNormalization\r\n')
    lens = []
    for i in range(len(gold)):
        string = str(i + 1)
        if len(str(i + 1)) <= 3:
            string += '\t\t' + str(len(gold[i])) + '\t\t\t' + str(metric1[i])
        else:
            string += '\t' + str(len(gold[i])) + '\t\t\t' + str(metric1[i])
        if len(str(metric1[i])) <= 3:
            string += '\t\t\t\t' + str(metric5[i])
        else:
            string += '\t\t\t' + str(metric5[i])
        if len(str(metric5[i])) <= 3:
            string += '\t\t\t\t' + str(metric2[i])
        else:
            string += '\t\t\t' + str(metric2[i])
        if len(str(metric2[i])) <= 3:
            string += '\t\t\t\t' + str(metric3[i])
        else:
            string += '\t\t\t' + str(metric3[i])
        if len(str(metric3[i])) <= 3:
            string += '\t\t\t\t' + str(metric4[i])
        else:
            string += '\t\t\t' + str(metric4[i])
        if len(str(metric4[i])) <= 3:
            string += '\t\t\t' + str(normalization[i]) + '\n'
        else:
            string += '\t\t' + str(normalization[i]) + '\n'
        lens.append(len(gold[i]))
        f.write(string)
    string2 = 'Avg.\t' + str(round((sum(lens)/len(lens)), 4)) + '\t\t' + str(round((sum(metric1)/len(metric1)), 4)) + '\t\t\t'
    string2 += str(round((sum(metric5)/len(metric5)), 4)) + '\t\t\t' + str(round((sum(metric2)/len(metric2)), 4)) + '\t\t\t'
    string2 += str(round((sum(metric3)/len(metric3)), 4)) + '\t\t\t' + str(round((sum(metric4)/len(metric4)),4)) + '\t\t'
    string2 += str(round((sum(normalization)/len(normalization)), 4)) + '\n'
    f.write(string2)
    f.close()

def compare_to_gold():
    parsed_path = input('The path to the parsed file: ')
    check_file(parsed_path)
    gold_path = input('The path to the gold file: ')
    check_file(gold_path)
    punct = input('Ignore punctuation in files? (yes/no) ')
    if punct == 'yes':
        parsed = make_tree(parsed_path)
        gold = make_tree(gold_path)
    else:
        parsed = make_tree_wo_pucntuation(parsed_path)
        gold = make_tree_wo_punctuation(gold_path)
    metric1 = accuracy(parsed, gold)
    metric2 = relations(parsed, gold)
    metric3 = ped(parsed, gold)
    metric4 = path_length(parsed, gold)
    metric5 = root_accuracy(parsed, gold)
    normalization = normalize(metric1, metric2, metric3, metric4, metric5)
    print('\nWriting result file')
    write_result('Result_with_gold.txt', gold, parsed, metric1, metric2, metric3, metric4, metric5, normalization)

def compare_to_generalized_gold():
    parsed_path = input('The path to the parsed file: ')
    check_file(parsed_path)
    gold_path = input('The path to the gold file for the parser: ')
    check_file(gold_path)
    gold_paths = [gold_path]
    n = int(input('\nHow many other gold standarts will contribute to the genralized gold standard? '))
    for i in range(n):
        gold_path = input('The path to the gold file: ')
        gold_paths.append(gold_path)
    golds = []
    punct = input('\nIgnore punctuation in files? (yes/no) ')    
    if punct == 'yes':
        parsed = make_tree(parsed_path)
        for g in gold_paths:
            gold = []
            gold = make_tree(g)
            golds.append(gold)
    else:
        parsed = make_tree_wo_punctuation(parsed_path)
        for g in gold_paths:
            gold = make_tree_wo_punctuation(g)
            golds.append(gold)
    print('\nCreating a generalized gold standard')
    for g in range(len(golds) - 1):
        generalized = generalize(golds[g], golds[g + 1])
        print('yes')
        golds[g + 1] = generalized
    metric1 = accuracy(parsed, gold)
    metric2 = relations(parsed, gold)
    metric3 = ped(parsed, gold)
    metric4 = span_difference(parsed, gold)
    metric5 = path_length(parsed, gold)
    normalization = normalize(metric1, metric2, metric3, metric4, metric5)
    print('\nWriting result file with the gold standard')
    write_result('Result_with_gold.txt', gold, parsed, metric1, metric2, metric3, metric4, metric5, normalization)
    metric1b = accuracy(parsed, golds[-1])
    metric2b = relations(parsed, golds[-1])
    metric3b = ped(parsed, golds[-1])
    metric4b = span_difference(parsed, golds[-1])
    metric5b = path_length(parsed, golds[-1])
    normalization2 = normalize(metric1b, metric2b, metric3b, metric4b, metric5b)
    print('\nWriting result file with the generalized gold standard')
    write_result('Result_with_generalized_gold.txt', gold, parsed, metric1b, metric2b, metric3b, metric4b, metric5b, normalization2)


def compare_two_parsers():
    parsed_path1 = input('The path to the first parsed file: ')
    check_file(parsed_path1)
    gold_path1 = input('The path to the gold file for the first parser: ')
    check_file(gold_path1)
    parsed_path2 = input('The path to the second parsed file: ')
    check_file(parsed_path2)
    gold_path2 = input('The path to the gold file for the second parser: ')
    check_file(gold_path2)
    punct = input('\nIgnore punctuation in files? (yes/no) ')    
    if punct == 'yes':
        parsed1 = make_tree(parsed_path1)
        parsed2 = make_tree(parsed_path2)
        gold1 = make_tree(gold_path1)
        gold2 = make_tree(gold_path2)
    else:
        parsed1 = make_tree_wo_punctuation(parsed_path1)
        parsed2 = make_tree_wo_punctuation(parsed_path2)
        gold1 = make_tree_wo_punctuation(gold_path1)
        gold2 = make_tree_wo_punctuation(gold_path2)
    print('\nCreating a generalized gold standard')
    generalized = generalize(gold1, gold2)
    metric1 = accuracy(parsed1, gold1)
    metric2 = relations(parsed1, gold1)
    metric3 = ped(parsed1, gold1)
    metric4 = span_difference(parsed1, gold1)
    metric5 = path_length(parsed1, gold1)
    normalization = normalize(metric1, metric2, metric3, metric4, metric5)
    print('\nWriting result file for the first parser with the gold standard')
    write_result('Result_with_gold_1.txt', gold1, parsed1, metric1, metric2, metric3, metric4, metric5, normalization)
    metric1b = accuracy(parsed2, gold2)
    metric2b = relations(parsed2, gold2)
    metric3b = ped(parsed2, gold2)
    metric4b = span_difference(parsed2, gold2)
    metric5b = path_length(parsed2, gold2)
    normalization2 = normalize(metric1b, metric2b, metric3b, metric4b, metric5b)
    print('\nWriting result file for the second parser with the gold standard')
    write_result('Result_with_gold_2.txt', gold2, parsed2, metric1b, metric2b, metric3b, metric4b, metric5b, normalization2)
    metric1c = accuracy(parsed1, generalized)
    metric2c = relations(parsed1, generalized)
    metric3c = ped(parsed1, generalized)
    metric4c = span_difference(parsed1, generalized)
    metric5c = path_length(parsed1, generalized)
    normalization3 = normalize(metric1c, metric2c, metric3c, metric4c, metric5c)
    print('\nWriting result file for the first parser with the generalized gold standard')
    write_result('Result_with_generalized_gold_1.txt', generalized, parsed1, metric1c, metric2c, metric3c, metric4c, metric5c, normalization3)
    metric1d = accuracy(parsed2, generalized)
    metric2d = relations(parsed2, generalized)
    metric3d = ped(parsed2, generalized)
    metric4d = span_difference(parsed2, generalized)
    metric5d = path_length(parsed2, generalized)
    normalization4 = normalize(metric1d, metric2d, metric3d, metric4d, metric5d)
    print('\nWriting result file for the second parser with the generalized gold standard')
    write_result('Result_with_generalized_gold_2.txt', generalized, parsed2, metric1d, metric2d, metric3d, metric4d, metric5d, normalization3)
