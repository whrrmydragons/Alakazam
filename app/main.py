from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date
import pandas  as pd
import os
import json
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation,performance_metrics
from starlette.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse, RedirectResponse

class Sample(BaseModel):
    ds: date
    y: float
    def to_dict(self):
        return {
            'ds': self.ds,
            'y': self.y,
        }
class Seasonality(BaseModel):
    name: str
    period: float
    fourier_order: int = 5
class Holiday(BaseModel):
    holiday: str
    ds: List[date]
    lower_window: int = 0
    upper_window: int = 1
class Predict(BaseModel):
    data: List[Sample]
    seasonalities: List[Seasonality]
    holidays: List[Holiday] = []
    periods: int = 365
    floor: int = 0
    only_predictions: bool  = True
    disable_diagnosis: bool = True

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def alakazam():
    response = RedirectResponse(url='/static/index.html')
    return response

@app.get("/isalive")
async def is_alive():
    return "alive"




'''
expect that the request contains a field name data which is an array containning objects of the following form:
{"ds":"2007-12-11","y":8.51959031601596}
'''
@app.post("/")
async def predict(body:Predict):
    data = body.data
    periods = body.periods
    holidays = createHolidays(body.holidays)
    seasonalities = body.seasonalities
    floor = body.floor

    #flag to disableDiagnosis
    disable_diagnosis = body.disable_diagnosis 
    # #turn the data recieved into a dataframe
    df = pd.DataFrame.from_records([d.to_dict() for d in data])
    # #set floor
    df['floor'] = floor
    #instinciate model
    m = initializeModel(holidays)
    # #if provided seasonalitied add them to the model before calling fit
    addSeasonalities(m,seasonalities)
    # #train/fit the model
    m.fit(df)
    #make a dataframe of future dates whos prediction we want to return to the user
    future = m.make_future_dataframe(periods=periods)
    if body.only_predictions:
        future = future[-periods:]
    #calculate future predictions a.k.a forecast
    forecast = m.predict(future)
    #return the forecast/prediction
    forecast = forecast.to_json(orient='records')

    ret = {}
    ret['forecast'] = json.loads(forecast)
    
    # if not disable_diagnosis:
    #     diagnostic(m=m,body=body,ret=ret)
    return ret

def createHolidays(holidays):
    holidays = [createHoliday(holiday) for holiday in holidays]
    if len(holidays)>0:
        holidays = pd.concat(holidays)
    return holidays
def createHoliday(holiday):
    return pd.DataFrame({
        'holiday': holiday.holiday,
        'ds':pd.to_datetime(holiday.ds),
        'lower_window': holiday.lower_window,
        'upper_window': holiday.upper_window,
    })
def addSeasonalities(m,seasonalities):
    for seasonality in seasonalities:
        name = seasonality.name
        period = seasonality.period
        fourier_order = seasonality.fourier_order
        m.add_seasonality(name=name, period=period, fourier_order=fourier_order)
def initializeModel(holidays):
    if len(holidays)>0:
        return Prophet(daily_seasonality=False,yearly_seasonality=False,weekly_seasonality=False,holidays=holidays) 
    else:
        return Prophet(daily_seasonality=False,yearly_seasonality=False,weekly_seasonality=False)
    