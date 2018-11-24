from flask import Flask, render_template
import envauth

app=Flask(__name__)

@app.route('/plot/')
def plot():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2018,9,1)
    end = datetime.datetime(2018,10,1)
    df = data.DataReader(name="TSLA", data_source="yahoo", start=start, retry_count=3)

    def inc_dec(c, o):
        if c > o:
            value="Increase"
        elif c < o:
            value="Decrease"
        else:
            value="Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
    df["Middle"] = (df.Open+df.Close)/2
    df["Height"] = abs(df.Close-df.Open) # abs gives positive

    p = figure(x_axis_type='datetime', width=1000, height=350, sizing_mode='scale_width')
    p.title.text = "Candlestick Chart"
    p.grid.grid_line_alpha = 0.3

    p.segment(df.index, df.High, df.index, df.Low, color="Black")

    hours_12 = 12*60*60*1000 # in milli for width

    increase = df.index[df.Close > df.Open]
    decrease = df.index[df.Close < df.Open]

    p.rect(df.index[df.Status=="Increase"], # Plot where close > open price
           df.Middle[df.Status=="Increase"], # mid point
           hours_12, # width
           df.Height[df.Status=="Increase"], # height
           fill_color="#32CD32",
           line_color="black"
          )

    p.rect(df.index[df.Status=="Decrease"],
           df.Middle[df.Status=="Decrease"],
           hours_12,
           df.Height[df.Status=="Decrease"],
           fill_color="#DC143C",
           line_color="black"
          )

    script_candle, div_candle = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files[0]
    return render_template("plot.html",
                           script_candle=script_candle,
                           div_candle=div_candle,
                           cdn_js=cdn_js,
                           cdn_css=cdn_css)
    

@app.route('/')
#@envauth.flask.requires_auth(realm='You shall not pass!')
def home():
    return render_template("home.html")

@app.route('/about/')
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
