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
    data = request.get_json(force=True)['data']
    df = pd.io.json.json_normalize(data)
    m = Prophet()
    m.fit(df)
    future = m.make_future_dataframe(periods=365)[-365:]
    forecast = m.predict(future)
    return forecast.to_json(orient='records')







if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)