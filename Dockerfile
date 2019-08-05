FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6
ADD ./app/requirements.txt /app/requirements.txt
RUN python3 -m pip install -r requirements.txt
COPY ./app /app
# CMD ["/start-reload.sh"] #use only for development