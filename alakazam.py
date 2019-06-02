import pandas  as pd
import json
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation,performance_metrics
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
    #create holidays
    holidays = createHolidays(body['holidays']) if 'holidays' in body else []
    #flag to disableDiagnosis
    disable_diagnosis = body['disable_diagnosis']=="true" if 'disable_diagnosis' in body else True
    #turn the data recieved into a dataframe
    df = pd.io.json.json_normalize(data)
    #instinciate model
    m = Prophet(holidays=holidays)
    #train/fit the model
    m.fit(df)
    #make a dataframe of future dates whos prediction we want to return to the user
    future = m.make_future_dataframe(periods=periods)[-periods:]
    #calculate future predictions a.k.a forecast
    forecast = m.predict(future)
    #return the forecast/prediction
    forecast = forecast.to_json(orient='records')

    ret = {}
    ret['forcast'] = json.loads(forecast)
    if not disable_diagnosis:
        diagnostic(m=m,body=body,ret=ret)
    return jsonify(ret)

#need 2 supply at least cv_horizon and cv_initial
def diagnostic(m,body,ret):
    #both parameters should be of the form <int> days/timeunit by timedelta
    cv_horizon = body['cv_horizon']
    cv_period = body['cv_period'] if 'cv_period' in body else False
    # cv_period = body['cv_period'] 
    #The initial period should be long enough to capture all 
    #of the components of the model,
    #in particular seasonalities and extra regressors: 
    #at least a year for yearly seasonality,
    #at least a week for weekly seasonality, etc.
    cv_initial = body['cv_initial']
    cv_args ={'initial':cv_initial,'horizon':cv_horizon}
    if cv_period:
        cv_args['period']=cv_period
    df_cv = cross_validation(m,**cv_args)
    cv = df_cv.to_json(orient='records')
    df_p = performance_metrics(df_cv)
    performance =df_p.to_json(orient='records')
    ret['cross_validation'] = json.loads(cv)
    ret['performance'] = json.loads(performance)
    return ret

def createHolidays(holidays):
    holidays = [createHoliday(holiday) for holiday in holidays]
    holidays = pd.concat(holidays)
    return holidays

def createHoliday(holiday):
    return pd.DataFrame({
        'holiday': holiday['holiday'],
        'ds':pd.to_datetime(holiday['ds']),
        'lower_window': holiday['lower_window'] if 'lower_window' in holiday else 0,
        'upper_window': holiday['upper_window'] if 'upper_window' in holiday else 1,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)