import _thread
import datetime
import json
import os
import time
from dotenv import load_dotenv

import requests
from flask import Flask, send_file, jsonify, request

app = Flask(__name__)


# WiFi_server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){             //Home Page
@app.route("/")
def home():
    return {'success': True}, 200, {'ContentType': 'application/json'}


# WiFi_server.on("/DwnLastFile", HTTP_GET, [](AsyncWebServerRequest *request){  //Download Last Acq file Request
@app.get("/DwnLastFile")
def download_last_file():
    try:
        return send_file(data_path)
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500, {'ContentType': 'application/json'}


# WiFi_server.on("/DwnFile", HTTP_GET, [](AsyncWebServerRequest *request){      //Download Last Data Acq file Request
@app.get("/DwnFile")
def download_file():
    try:
        return send_file(data_path)
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500, {'ContentType': 'application/json'}


@app.get("/Restart")
def restart():
    try:
        _thread.start_new_thread(register_dev_thread, (35,))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        print(e)
        return jsonify({'success': False}), 500, {'ContentType': 'application/json'}


@app.get('/parametersReq')
def get_config():
    return jsonify(curr_config), 200, {'ContentType': 'application/json'}


@app.get('/get')
def get():
    if 'currentTime' in request.args:
        # 2023-09-26T20:17
        d = datetime.datetime.strptime(request.args.get('currentTime'), "%Y-%m-%dT%H:%M")
        # 2023-10-4 15:17
        curr_config['JsCurrentTime'] = d.strftime("%Y-%m-%d %H:%M")
    elif 'objAcqTimeIN' in request.args:
        curr_config['JsAcqTime'] = int(request.args.get('objAcqTimeIN'))
    elif 'alarm1H' in request.args:
        curr_config['JsDailyAlarm'] = f"{request.args.get('alarm1H')}:{request.args.get('alarm1m')}"
    elif 'objThrsXValIN' in request.args:
        curr_config['JsThrsValX'] = int(request.args.get('objThrsXValIN'))
    elif 'objThrsYValIN' in request.args:
        curr_config['JsThrsValY'] = int(request.args.get('objThrsYValIN'))
    elif 'objPreAcqTimeIN' in request.args:
        curr_config['JsAcqTime'] = int(request.args.get('objPreAcqTimeIN'))

    return jsonify({
        "JsThrsValX": curr_config['JsThrsValX'],
        "JsThrsValY": curr_config['JsThrsValY'],
        "JsHVVal": curr_config['JsHVVal'],
        "JsHVRead": curr_config['JsHVRead'],
        "JsAcqTime": curr_config['JsAcqTime'],
        "JsPreAcqTime": curr_config['JsPreAcqTime'],
        "JsDailyAlarm": curr_config["JsDailyAlarm"],
        "JsAlarmAdjust": "No",
        "JsWathAdjusted": "No",
        "JsWiFiUpdated": "No"
    }), 200, {'ContentType': 'application/json'}


def register_dev_thread(sleep_time=2):
    time.sleep(sleep_time)
    print(f'register_dev with thread ')
    print("it's time to register the device!")
    # registro il device
    requests.get(f'http://{server_ip}:1221/register_device?dev={devname}&port={port}')
    print(f'registro device {devname} - 127.0.0.1:{port}')
    # dico che le misure sono pronte
    requests.get(f'http://{server_ip}:1221/data_is_ready?port={port}')


def run_app_thread():
    print(f'run_app with thread ')
    app.run(host='0.0.0.0', port=port)


devname = '01X'
port = 80  # use your port
curr_config = {"JsThrsValX": 200, "JsThrsValY": 200, "JsHVVal": 1300, "JsHVRead": 0, "JsAcqTime": 10000,
               "JsPreAcqTime": 15000, "JsDailyAlarm": "11:30",
               "JsCurrentTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
server_ip = ''  # use your ip

if __name__ == '__main__':
    load_dotenv()
    data_path = os.environ.get("DATA_PATH")
    ascii_data_path = os.environ.get("ASCII_DATA_PATH")
    try:
        _thread.start_new_thread(run_app_thread, ())
        _thread.start_new_thread(register_dev_thread, ())
    except Exception as e:
        print(f'unable to start threads: {e}')
    while 1:
        pass
