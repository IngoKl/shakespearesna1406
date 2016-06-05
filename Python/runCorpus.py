import ShakespeareSnaAnalysis as sna
import os

"""Settings"""
corpus_dir = '../../Corpus/'

counter = 0
if not os.path.exists('results'):
    os.mkdir('results')
    print 'Directory "results" has been created'

if os.path.isfile('results/allCharacters.csv'):
    choice = raw_input('Should "allCharacters.csv" be deleted before continuing? [yes or no]: ').lower()
    if choice == 'yes':
        os.remove('results/allCharacters.csv')
    else:
        os.rename('results/allCharacters.csv', 'results/allCharacters.csv-bu')
        print ('The file has been renamed to "results/allCharacters.csv-bu"')

for file in os.listdir(corpus_dir):
    if file.endswith('.txt'):
        counter += 1
        print '[%d / %d] %s' % (counter, len(os.listdir(corpus_dir)), file)
        if os.path.isfile(corpus_dir + file):
            sna.sna_calculations(sna.characters_in_scene(corpus_dir + file), corpus_dir + file)
        else:
            print 'File does not exist!'
