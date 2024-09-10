FROM python:3.10.13-alpine3.18

COPY requirements.txt ./

#RUN apt-get install libpq-dev python3-dev postgresql-libs gcc libc-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY  app.py ./home/app.py


ENV TZ=CET
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR home/
CMD ["python3","app.py"]
