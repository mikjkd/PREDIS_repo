FROM python:3.10.13-alpine3.18

COPY core/requirements.txt ./

RUN pip install postgres
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY  . ./home/PREDIS_project/codice/backend/
COPY  config/predis.env ./home/PREDIS_project/codice/backend/core/predis.env

ENV TZ=CET
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONPATH "${PYTHONPATH}:/home/PREDIS_project/"

EXPOSE 1221
WORKDIR home/
RUN mkdir -p PREDIS_project/devices
#CMD ["python","PREDIS_project/codice/app.py"]
CMD gunicorn --bind 0.0.0.0:1221 --chdir PREDIS_project/codice/backend/ wsgi:app



