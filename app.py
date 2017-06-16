from flask import Flask, render_template, request, redirect
from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.util.string import encode_utf8
import simplejson as sj
import collections
#import numpy as np
import pandas as pd
import requests
import os

app = Flask(__name__)

app.vars={}

#capture the dates with the Qdate2 function
def Qdate2():
    
    from datetime import date
    d2 = date.today()
    
    last_month = len(str(d2.month-1))
    if last_month < 2 :
        ymlast = str(d2.year) + str(0) + str(d2.month -1) 
    else :
        ymlast = str(d2.year) + str(d2.month-1)

    last_day = len(str(d2.day))
    if last_day < 2:
        my_date_last = ymlast + str(0) + str(d2.day)
    else:
        my_date_last = ymlast + str(d2.day)

    this_month = len(str(d2.month))
    if this_month <2:
        ym = str(d2.year) + str(0) + str(d2.month)
    else:
        ym = str(d2.year) + str(d2.month)
    
    this_day = len(str(d2.day))
    if this_day < 2:
        my_date = ym + str(0) + str(d2.day)
    else:
        my_date = ym + str(d2.day)   
    
    return my_date_last, my_date

dates = Qdate2()
lastmth = dates[0]
thismth = dates[1]

#Define the function that capture the stock price data

def ticker_select(name):
    
    url = "https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json"
    payload = {
        'api_key':'HU364vGPSQwLaZQ_qKFz',
        'date.gte':lastmth,
        'date.lte':thismth,
        'ticker': name,
        'qopts.columns':'ticker,''date,''close'
    }
    r=requests.get(url, params = payload)
    return r.text


@app.route('/index', methods=['GET','POST'])
def index():
    
    if request.method == 'GET':
        return render_template('homescreen.html')
        
    else:
        #request was a POST
        app.vars['symbol'] = request.form['ticker']
        mydata = ticker_select(app.vars['symbol'])
        mydict = sj.loads(mydata)
        
        def convert(data):
            if isinstance(data, basestring):
                return str(data)
            elif isinstance(data, collections.Mapping):
                return dict(map(convert, data.iteritems()))
            elif isinstance(data, collections.Iterable):
                return type(data)(map(convert, data))
            else:
                return data

        dict1 = convert(mydict)
        df = pd.DataFrame(dict1['datatable']['data'], columns=['ticker', 'date','close'])
        df['date'] = pd.to_datetime(df['date'])
        #df.set_index('date')
        
        p1 = figure(x_axis_type="datetime", title="Stock Closing Prices")
        p1.grid.grid_line_alpha=0.3
        p1.xaxis.axis_label = 'Date'
        p1.yaxis.axis_label='Price'

        p1.line(df['date'], df['close'], color='#A6CEE#',
                legend=df['ticker'][0])
        p1.legend.location = "top_left"
        
        script, div = components(p1)

               
        return encode_utf8(render_template('plotview.html', script=script, div=div))
       

if __name__== "__main__":
    port = int(os.environ.get("PORT", 33507))
    app.run(host='0.0.0.0', port=port)