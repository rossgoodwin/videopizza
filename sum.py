from collections import Counter
import re
import string
from sys import argv
import en

script, subfile = argv

textFile = open(subfile, 'r')
subText = textFile.read()
textFile.close()

allSubLines = subText.split('\n')

textLines = []

for line in allSubLines:
    if len(line) > 0 and line[0] in string.ascii_letters:
        textLines.append(line)

text = ' '.join(textLines)

accept_pos = ['NN', 'NNP', 'NNPS', 'NNS', 'NP', 'RB', 'RBR', 'RBS', 'VA', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP', 'JJ', 'JJR', 'JJS']
stop_words =  ["!", "$", "%", "&", ",", "-", ".", "0", "1", "10", "100", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2", "20", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "21", "22", "23", "24", "25", "26", "27", "28", "29", "3", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "4", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "5", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "6", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "7", "70", "71", "72", "73", "74", "75", "76", "77", "78", "8", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "9", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", ":", ";", "<", ">", "@", "\(", "\)", "\*", "\+", "\?", "\[", "\]", "\^", "\{", "\}", "a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "b", "back", "be", "because", "been", "before", "beforehand", "being", "beside", "besides", "between", "both", "bottom", "but", "by", "c", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "d", "de", "did", "didn't", "do", "does", "doesn't", "don't", "done", "down", "due", "during", "e", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "f", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "g", "get", "give", "go", "h", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed", "into", "is", "it", "its", "itself", "j", "k", "keep", "l", "last", "latter", "latterly", "least", "less", "ltd", "m", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "n", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "o", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "p", "part", "per", "perhaps", "please", "put", "q", "r", "rather", "re", "s", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "since", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "t", "take", "ten", "than", "that", "the", "thee", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thing", "third", "this", "those", "thou", "though", "three", "through", "throughout", "thru", "thus", "thy", "to", "together", "too", "toward", "towards", "twelve", "twenty", "two", "u", "un", "under", "until", "up", "upon", "us", "v", "very", "via", "w", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "x", "y", "yet", "you", "your", "yours", "yourself", "yourselves", "z", "|"]

pos = en.sentence.tag(text)
wordtag = map(list, zip(*pos))
words, tags = wordtag

imp_words = [words[i] for i in range(len(words)) if tags[i] in accept_pos and not words[i] in stop_words]

word_counts = dict(Counter(imp_words).most_common())

for w in words:
    if not w in word_counts.keys():
        word_counts[w] = 0

# word_map = [(w, word_counts[w]) for w in words]
endPunc = ['.', '?', '!']

sentences = re.split(r'!|\?|\.', text)
sentences = [s for s in sentences if s]

print len(sentences)

sentenceScores = []
sentenceLengths = []

curSentenceScore = 0
curSentenceLength = 0

for w in words:
    curSentenceScore += word_counts[w]
    curSentenceLength += 1
    if w[-1] in endPunc or "." in w:
        sentenceScores.append(curSentenceScore)
        sentenceLengths.append(curSentenceLength)
        curSentenceScore = 0
        curSentenceLength = 0

print len(sentenceScores)
print len(sentenceLengths)

if len(sentences) == len(sentenceScores) == len(sentenceLengths):
    print "EVERYTHING WORKED!"
else:
    print "SOMETHING BROKE!"

normSentenceScores = [{'index': i, 'score': sentenceScores[i]} for i in range(len(sentences))]

normSentenceScores.sort(key=lambda x:x['score'], reverse=True)

print normSentenceScores

tgtIndx = [d['index'] for d in normSentenceScores[:10]]
tgtIndx.sort()

for i in tgtIndx:
    print sentences[i]
    print sentenceScores[i]




