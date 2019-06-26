import pandas  as pd
import os
import json
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation,performance_metrics
from flask import jsonify,Flask,request,send_from_directory

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')

#helper functions
def getField(body,field_name,default_value):
    return body[field_name] if field_name in body else default_value

app = Flask(__name__,static_folder=static_file_dir,static_url_path='')

#Environment Variables
port = os.environ['PORT'] if 'PORT' in os.environ else 8080
debug = os.environ['DEBUG']=="true" if 'DEBUG' in os.environ else True

#Routes


@app.route("/",methods=['GET'])
def serve_reveal():
    return send_from_directory(static_file_dir, 'index.html')


'''
expect that the request contains a field name data which is an array containning objects of the following form:
{"ds":"2007-12-11","y":8.51959031601596}
'''
@app.route("/", methods=['POST'])
def predict():
    #get the parsed request`s body
    body = request.get_json(force=True)
    #get the data parameter from the body
    data = getField(body=body,field_name="data",default_value=[])
    #get the periods parameter from the body
    #if its undefined its default value will be 365 steps 
    periods = getField(body=body,field_name='periods',default_value=365)
    #create holidays
    holidays = createHolidays(getField(body=body,field_name='holidays',default_value=[]))
    #create custom Seasonalities if provided
    seasonalities = getField(body=body,field_name='seasonalities',default_value=[])
    #flag to disableDiagnosis
    disable_diagnosis = body['disable_diagnosis']=="true" if 'disable_diagnosis' in body else True
    #turn the data recieved into a dataframe
    df = pd.io.json.json_normalize(data)
    #TODO get this as a flag/variable
    #set floor
    df['floor'] = 0
    #instinciate model
    #TODO: change to argument dictionary like in diagnostic
    m = Prophet(daily_seasonality=False,yearly_seasonality=False,weekly_seasonality=False,holidays=holidays) if len(holidays)>0 else Prophet()
    #if provided seasonalitied add them to the model before calling fit
    addSeasonalities(m,seasonalities)
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
    if len(holidays)>0:
        holidays = pd.concat(holidays)
    return holidays

def createHoliday(holiday):
    return pd.DataFrame({
        'holiday': holiday['holiday'],
        'ds':pd.to_datetime(holiday['ds']),
        'lower_window': holiday['lower_window'] if 'lower_window' in holiday else 0,
        'upper_window': holiday['upper_window'] if 'upper_window' in holiday else 1,
    })
def addSeasonalities(m,seasonalities):
    for seasonality in seasonalities:
        name = seasonality['name']
        period = seasonality['period']
        fourier_order = seasonality['fourier_order'] if 'fourier_order' in seasonality else 5
        m.add_seasonality(name=name, period=period, fourier_order=fourier_order)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port,debug=debug)