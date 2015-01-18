from __future__ import print_function

import argparse
from collections import Counter
from lxml import etree, html
import re
import requests
import subprocess
import sys
from moviepy.editor import *
import en


def getProgid(pageurl):
    page = html.parse(pageurl).getroot()
    ve = page.get_element_by_id("video-embed")
    return ve.get("data-progid")

def getCapUrl(progid):
    params = {"os": "html",
              "html5": "program",
              "id": progid}
    obj = requests.get("http://www.c-span.org/assets/player/ajax-player.php",params=params).json()
    return obj['video']['capfile']['#text']

def parseTTML(url):
    root = etree.parse(url).getroot()
    atoms = []
    for p in root.iter("{http://www.w3.org/ns/ttml}p"):
        atom = {"begin":p.get("begin") , "end":p.get("end"), "lines":[p.text or '']}
        for br in p.iter("{http://www.w3.org/ns/ttml}br"):
            atom['lines'].append(br.tail or '')
        atoms.append(atom)
    return atoms

def ttmlToLines(atoms,narrow_mode=True):
    lines = []
    running_line = None
    for atom in atoms:
        if running_line is not None and atom['lines'][-1].startswith(running_line):
            if atom['lines'][-1] != running_line:
                if narrow_mode:
                    diff = atom['lines'][-1][len(running_line):]
                    lines.append({'begin':atom['begin'], 'end':atom['end'], 'text': diff})
                else:
                    lines[-1]['text'] = atom['lines'][-1]
                    lines[-1]['end'] = atom['end']
            running_line = atom['lines'][-1]
        else:
            lines.append({'begin':atom['begin'] or 0, 'end':atom['end'], 'text': atom['lines'][-1]})
            running_line = atom['lines'][-1]
    return lines
    
def linesToSentences(lines):
    s = None
    sentences = []
    for l in lines:
        explode = re.findall(r"[\w']+|[.!?]",l['text'])
        for tok in explode:
            if re.match(r"[.!?]",tok) is not None:
                sentences.append(s)
                s = None
            else:
                if s is None:
                    s = {'begin':l['begin'], 'end':l['end'], 'words':[tok]}
                else:
                    s['words'].append(tok)
                    s['end']=l['end']
    if s is not None:
        sentences.append(s)
    return sentences

def summarizeSentences(sentences,count=12):
    accept_pos = set(['NN', 'NNP', 'NNPS', 'NNS', 'NP', 'RB', 'RBR', 'RBS', 'VA', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VP', 'JJ', 'JJR', 'JJS'])
    stop_words =  set(["!", "$", "%", "&", ",", "-", ".", "0", "1", "10", "100", "11", "12", "13", "14", "15", "16", "17", "18", "19", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2", "20", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "21", "22", "23", "24", "25", "26", "27", "28", "29", "3", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "4", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "5", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "6", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "7", "70", "71", "72", "73", "74", "75", "76", "77", "78", "8", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "9", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99", ":", ";", "<", ">", "@", "\(", "\)", "\*", "\+", "\?", "\[", "\]", "\^", "\{", "\}", "a", "about", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "b", "back", "be", "because", "been", "before", "beforehand", "being", "beside", "besides", "between", "both", "bottom", "but", "by", "c", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "d", "de", "did", "didn't", "do", "does", "doesn't", "don't", "done", "down", "due", "during", "e", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "f", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "g", "get", "give", "go", "h", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed", "into", "is", "it", "its", "itself", "j", "k", "keep", "l", "last", "latter", "latterly", "least", "less", "ltd", "m", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "n", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "o", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "p", "part", "per", "perhaps", "please", "put", "q", "r", "rather", "re", "s", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "since", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "t", "take", "ten", "than", "that", "the", "thee", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thing", "third", "this", "those", "thou", "though", "three", "through", "throughout", "thru", "thus", "thy", "to", "together", "too", "toward", "towards", "twelve", "twenty", "two", "u", "un", "under", "until", "up", "upon", "us", "v", "very", "via", "w", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "x", "y", "yet", "you", "your", "yours", "yourself", "yourselves", "z", "|"])
    wordscore = Counter()
    for s in sentences:
        s['tagged']=[(w,t) for w,t in en.sentence.tag(" ".join(s['words'])) if w not in stop_words and t in accept_pos]
        wordscore.update(s['tagged'])
    for s in sentences:
        s['score'] = sum([wordscore[w] for w in s['tagged']])
    sentences.sort(key=lambda x:x['score'], reverse=True)
    return sentences[:count]

def makeGifs(sentences):
    clip = VideoFileClip("../../foo.mp4", audio=False)
    out = []
    for i,s in enumerate(sentences):
        clip.subclip(float(s['begin']),float(s['end']))
        # clip.to_gif('gifs/%d.gif'%i, fps=1)
        # txt_clip = ( TextClip(" ".join(s['words']),fontsize=70,color='white')
        #      .set_position('center')
        #      .set_duration(15) )

        # result = CompositeVideoClip([clip, txt_clip])
        fn = 'static/gifs/%d.mp4'%i
        clip.to_videofile(fn, codec="libx264")
        fns.append(fn)
    return fns


def fmtSrtTime(secs):
    fsecs = float(secs)
    isecs = int(fsecs)
    ms = 1000 * (fsecs-isecs)
    s = isecs%60
    m = (isecs/60)%60
    h = isecs/(60*60)
    return "%02d:%02d:%02d,%03d" % (h,m,s,ms)

def buildSrt(lines):
    if sys.argv[2]=='-':
        fh = sys.stdout
    else:
        fh = open(sys.argv[2],'w')
    for i,l in enumerate(lines,start=1):
        print(i,file=fh)
        print("%s --> %s" % (fmtSrtTime(l['begin']),fmtSrtTime(l['end'])),file=fh)
        print(l['text'],file=fh)
        print('',file=fh)
    fh.close()

def processUrl(url):
    return makeGifs(
        summarizeSentences(
            linesToSentences(
                ttmlToLines(
                    parseTTML(
                        getCapUrl(
                            getProgid(url)))))))

if __name__ == "__main__":
    if len(sys.argv)<1:
        print("Usage: cspan.py cspanurl")
    else:
        processUrl(sys.argv[1])
        # makeGifs(summarizeSentences(linesToSentences(ttmlToLines(parseTTML(getCapUrl(getProgid(sys.argv[1]))),True))))
        # buildSrt(ttmlToLines(parseTTML(getCapUrl(getProgid(sys.argv[1]))),narrow_mode))





