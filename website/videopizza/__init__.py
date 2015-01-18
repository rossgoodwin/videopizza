from flask import Flask
from flask import render_template
from flask import request
from time import sleep

import sys
sys.path.append("../..")
import cspan

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/sum", methods=['POST'])
def summary():
	if request.method == 'POST':
		vidURL = request.form['videourl']
		gifNames = cspan.processUrl(vidURL)

		return render_template("gifs.html", gif1=gifNames[0], gif2=gifNames[1], gif3=gifNames[2], 
											gif4=gifNames[3], gif5=gifNames[4], gif6=gifNames[5], 
											gif7=gifNames[6], gif8=gifNames[7], gif9=gifNames[8],
											gif10=gifNames[9], gif11=gifNames[10], gif12=gifNames[11])
	else:
		return "You didn't say the magic word."

def processUrl(url):
	return [str(i)+'.mp4' for i in range(12)]

if __name__ == "__main__":
    app.run()


