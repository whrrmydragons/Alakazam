# [Alakazam](https://whrrmydragons.github.io/Alakazam/)
REST Wrap for fbprophet

<img src="https://whrrmydragons.github.io/Alakazam/alakazam_animated%20.svg" alt="drawing" width="30%" height="10%"/>

---

# Getting Started
You can either use:
* the provided docker compose (build localy or pull from [dockerhub](https://hub.docker.com/r/rabiran/alakazam)) 
* use a python environment with pandas flask and fbprophet.

----

Run the Server by running the following command:
```
python alakazam.py
```
the server runs on 8080

---

# Routes
Currently there is only a single route "post http://alakazam_url_or_ip:8080/".

----
## Request Parameters
| Name  | Required |Description |
| ------------- | ------------- |------------- |
| data  |&#9745; |An Array of sample objects of the following form: {ds:"date",y:(numeric value)} | 
| disable_diagnosis  | &#9744;   |Flag to disable diagnosis which tends to be slow. Defaults to true. |

----

| Name  | Required |Description |
| ------------- | ------------- |------------- |
| cv_horizon  | &#9745; IFF disable_diagnosis is false  |cross validation forecast horizon  |
| cv_initial  | &#9745; IFF disable_diagnosis is false  |he size of the initial training period  |
| cv_period  | &#9744;   |the spacing between cutoff dates  |

----

| Name  | Required |Description |
| ------------- | ------------- |------------- |
| holidays  | &#9744; |Array of holidays objects, each of the following structure {"holiday": "holiday_name","ds": ["2010-02-07", "2014-02-02", "2016-02-07","2016-01-20""2016-01-21","2016-01-22"],"lower_window": 0,"upper_window": 1}}  |

----

| Name  | Required |Description |
| ------------- | ------------- |------------- |
| seasonalities  | &#9744; |Array of Seasonalities each is an object of the following structure {"name":"season_name","period":(numeric_value),"fourier_order"(positive integer)}. If fourier_order default value is 5, name and period are required |
