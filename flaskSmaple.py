# Flask code :
#pip install

from flask import Flask
app = Flask(__name__)

@app.route('/vehicle/speed/<string:value>')
def speedControl(value):
   return f'Value is {value}'


app.run("localhost", 5000)