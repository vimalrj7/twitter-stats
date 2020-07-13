from flask import Flask, render_template, request
from plot import create_plots
import random

app = Flask(__name__)
app.config.from_object('config.ProdConfig')


@app.route('/', methods=['GET', 'POST'])
def index():
    plots = []
    home_page = ['@NASA', '@BarackObama', '@KingJames', '@ladygaga', 
    '@britneyspears', '@BillGates', '@Drake']
    screen_name = ''
    
    error = False

    if request.method == 'POST':
        
        screen_name = request.form['twhandle']
        if screen_name[0] != '@':
            screen_name = '@' + screen_name

        try:
            plots = create_plots(screen_name)
        except:
            error = True
    else:
        screen_name = random.choice(home_page)
        plots = create_plots(screen_name)

    return render_template('dash.html', plots=plots, screen_name=screen_name, error=error)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run() 