import pandas  as pd
from fbprophet import Prophet
from flask import jsonify,Flask,request
app = Flask(__name__)


'''
expect that the request contains a field name data which is an array containning objects of the following form:
{"ds":"2007-12-11","y":8.51959031601596}
'''
@app.route("/", methods=['POST'])
def predict():
    #get the parsed request`s body
    body = request.get_json(force=True)
    #get the data parameter from the body
    data = body['data']
    #get the periods parameter from the body
    #if its undefined its default value will be 365 steps 
    periods = body['periods'] if 'periods' in body else 365
    #turn the data recieved into a dataframe
    df = pd.io.json.json_normalize(data)
    #instinciate model
    m = Prophet()
    #train/fit the model
    m.fit(df)
    #make a dataframe of future dates whos prediction we want to return to the user
    future = m.make_future_dataframe(periods=periods)[-periods:]
    #calculate future predictions a.k.a forecast
    forecast = m.predict(future)
    #return the forecast/prediction
    return forecast.to_json(orient='records')







if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)