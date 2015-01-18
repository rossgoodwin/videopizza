from __future__ import print_function

import argparse
from lxml import etree, html
import requests
import sys


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

def ttmlToLines(atoms,narrow_mode=False):
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

narrow_mode=False
buildSrt(ttmlToLines(parseTTML(getCapUrl(getProgid(sys.argv[1]))),narrow_mode))





