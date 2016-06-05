import collections
import csv
import os.path
import re
from collections import defaultdict
import networkx as nx
import numpy
import sys


def sna_calculations(g, play_file):
    """
    :param g: a NetworkX graph object
    :type g: object
    :param play_file: the location of a play in .txt format
    :type play_file: string
    :return: returns a dictionary containing various network related figures
    :rtype: dict
    :note: also writes into results/file_name-snaCalculations.csv and results/allCharacters.csv
    """
    file_name = os.path.splitext(os.path.basename(play_file))[0]
    sna_calculations_list = dict()
    sna_calculations_list['playType'] = file_name[0]
    sna_calculations_list['avDegreeCentrality'] = numpy.mean(numpy.fromiter(iter(nx.degree_centrality(g).values()),
                                                                            dtype=float))
    sna_calculations_list['avDegreeCentralityStd'] = numpy.std(
        numpy.fromiter(iter(nx.degree_centrality(g).values()), dtype=float))
    sna_calculations_list['avInDegreeCentrality'] = numpy.mean(
        numpy.fromiter(iter(nx.in_degree_centrality(g).values()), dtype=float))
    sna_calculations_list['avOutDegreeCentrality'] = numpy.mean(
        numpy.fromiter(iter(nx.out_degree_centrality(g).values()), dtype=float))

    try:
        sna_calculations_list['avShortestPathLength'] = nx.average_shortest_path_length(g)
    except:
        sna_calculations_list['avShortestPathLength'] = 'not connected'

    sna_calculations_list['density'] = nx.density(g)
    sna_calculations_list['avEigenvectorCentrality'] = numpy.mean(
        numpy.fromiter(iter(nx.eigenvector_centrality(g).values()), dtype=float))
    sna_calculations_list['avBetweennessCentrality'] = numpy.mean(
        numpy.fromiter(iter(nx.betweenness_centrality(g).values()), dtype=float))
    sna_calculations_list['DegreeCentrality'] = nx.degree_centrality(g)
    sna_calculations_list['EigenvectorCentrality'] = nx.eigenvector_centrality(g)
    sna_calculations_list['BetweennessCentrality'] = nx.betweenness_centrality(g)

    # sna_calculations.txt file
    sna_calc_file = csv.writer(open('results/' + file_name + '-snaCalculations.csv', 'wb'), quoting=csv.QUOTE_ALL,
                               delimiter=';')
    for key, value in sna_calculations_list.items():
        sna_calc_file.writerow([key, value])

    # all_characters.csv file
    if not os.path.isfile('results/allCharacters.csv'):
        with open('results/allCharacters.csv', 'w') as f:
            f.write(
                'Name;PlayType;play_file;DegreeCentrality;EigenvectorCentrality;BetweennessCentrality;speech_amount;AverageUtteranceLength\n')

    all_characters = open('results/allCharacters.csv', 'a')
    character_speech_amount = speech_amount(play_file)
    for character in sna_calculations_list['DegreeCentrality']:
        all_characters.write(character + ';' + str(sna_calculations_list['playType']) + ';' + file_name + ';' + str(
            sna_calculations_list['DegreeCentrality'][character]) + ';' + str(
            sna_calculations_list['EigenvectorCentrality'][character]) + ';' + str(
            sna_calculations_list['BetweennessCentrality'][character]) + ';' + str(
            character_speech_amount[0][character]) + ';' + str(character_speech_amount[1][character]) + '\n')
    all_characters.close()

    return sna_calculations


def speech_amount(play_file):
    """
    :param play_file: the location of a play in .txt format
    :type play_file: string
    :return: returns a list containing the result_array and the result_array_length
    :rtype: list
    :note: also writes into results/file_name-speechAmountTable.csv
    """
    file_name = os.path.splitext(os.path.basename(play_file))[0]
    character_array = []
    result_array = collections.OrderedDict()
    result_array_length = collections.OrderedDict()
    length_total = 0

    with open(play_file) as play:
        regex = re.compile(r'<((?!/)(?!STAGE DIR)(?!Enter)(?!ACT)(?!SCENE)(?!Exit)(?!EPILOGUE)[A-Z0-9 ]*?)>')

        for line in play:
            line_re = regex.search(line)
            if line_re is not None:
                character_array.append(line_re.group(1))

    with open(play_file) as play:
        character_array = sorted(set(character_array))  # Deduplicate; All characters
        play_text = play.read()
        for character in character_array:
            result_array[character] = 0
            result_array_length[character] = 0
            result_array_length_temp = []
            # regex = re.compile(r'<'+character+'>(.*?)</'+character+'>')
            regex = re.compile(r'<%s>(.*?)</%s>' % (character, character), re.MULTILINE | re.DOTALL)
            character_result = re.findall(regex, play_text)
            for result in character_result:
                result_array_length_temp.append(len(result))
                result_array[character] += len(result)
                result_array_length[character] = numpy.average(result_array_length_temp)  # Average Utterance Length

    table = open('results/' + file_name + '-speechAmountTable.csv', 'w')
    table.write('Character;Length;avg. Utterance Length;Percent\n')

    for result in result_array:
        length_total = length_total + result_array[result]
    for result in result_array:
        table.write(result + ';' + str(result_array[result]) + ';' + str(result_array_length[result]) + ';' + str(
            float(float(result_array[result]) / length_total * 100)) + '\n')

    table.close()
    return [result_array, result_array_length]


def characters_in_scene(play_file):
    """
    :param play_file: the location of a play in .txt format
    :type play_file: string
    :return: returns a NetworkX graph object
    :rtype: object
    :note: also writes into results/file_name-affiliationMatrix.csv, -network.gexf, and network.graphml
    """

    file_name = os.path.splitext(os.path.basename(play_file))[0]
    current_act = 0
    current_scene = 0
    result_array = defaultdict(lambda: defaultdict(dict))
    act_scene_array = []
    character_array = []
    character_speech_amount = speech_amount(play_file)

    with open(play_file) as play:
        for line in play:
            if line[0:4] == '<ACT':
                if int(line[5]) > current_act:
                    current_act = int(line[5])

            # What follows is a really bad hack to recognize roman numerals - better done than perfect ... for now
            if line[0:6] == '<SCENE':
                if line[7] == 'X' and line[8] == 'I' and line[9] == 'I' and line[10] == 'I':
                    scene_no = 13
                elif line[7] == 'X' and line[8] == 'I' and line[9] == 'I':
                    scene_no = 12
                elif line[7] == 'X' and line[8] == 'I':
                    scene_no = 11
                elif line[7] == 'X' and line[8] == '.':
                    scene_no = 10
                else:
                    scene_no = int(line[7])

                if scene_no > current_scene:
                    current_scene = scene_no

            regexp = re.compile(r'<((?!/)(?!STAGE DIR)(?!Enter)(?!ACT)(?!SCENE)(?!Exit)(?!EPILOGUE)[A-Z0-9 ]*?)>')
            line_re = regexp.search(line)
            if line_re is not None:
                result_array[str(current_act) + '#' + str(current_scene)][line_re.group(1)] = 1
                act_scene_array.append(str(current_act) + '#' + str(current_scene))
                character_array.append(line_re.group(1))

    act_scene_array = sorted(set(act_scene_array))  # Deduplicate
    character_array = sorted(set(character_array))  # Deduplicate; All characters

    # CSV and NetworkX
    csv_file = open('results/' + file_name + '-affiliationMatrix.csv', 'w')
    g = nx.DiGraph()

    csv_headline = 'Act#Scene'
    for act_scene_combo in act_scene_array:
        csv_headline = csv_headline + ';' + act_scene_combo

    # print csv headline
    csv_file.write(csv_headline + '\n')

    for character in character_array:
        csv_line = character
        g.add_node(character, length=character_speech_amount[0][character])

        for act_scene_combo in act_scene_array:
            if character in result_array[act_scene_combo]:
                csv_line += ';1'

                for othercharacter in result_array[act_scene_combo]:  # Adding to the NetworkX g
                    if g.has_edge(character, othercharacter):
                        g[character][othercharacter]['weight'] += 1
                    else:
                        g.add_edge(character, othercharacter, weight=1)
            else:
                csv_line += ';0'

        # print individual csv lines
        csv_file.write(csv_line + '\n')
        nx.write_gexf(g, 'results/' + file_name + '-network.gexf')
        nx.write_graphml(g, 'results/' + file_name + '-network.graphml')

    csv_file.close()
    return g


# This is how the script is initialized if it is not called by runCorpus.py
if sys.argv[0] == 'ShakespeareSnaAnalysis':
    try:
        if sys.argv[1]:
            if not os.path.exists('results'):
                os.mkdir('results')
                print 'Directory "results" has been created'

            if os.path.isfile(sys.argv[1]):
                print 'Analzying: ' + sys.argv[1]
                sna_calculations(characters_in_scene(sys.argv[1]), sys.argv[1])
            else:
                print 'File does not exist!'
    except:
        print 'Usage: ShakespeareSnaAnalysis.py file_name.txt'
