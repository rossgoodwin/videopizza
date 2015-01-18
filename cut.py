from videogrep import videogrep
from sys import argv

script, inputfile, outputfile, search, padding, sync = argv

videogrep(inputfile, outputfile, search, 're', 1, int(padding), False, True, sync)



