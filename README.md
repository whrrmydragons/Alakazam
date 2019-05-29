# Alakazam
REST Wrap to fbprophet

---

# Getting Started
You can either use:
* the provided docker compose (build localy or pull from dockerhub) 
* use a python environment with pandas flask and fbprophet.

----

Run the Server by running the following command:
```
python alakazam.py
```
the server runs on 8080

---

# Routes
Currently there is only a single route "post /".

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
