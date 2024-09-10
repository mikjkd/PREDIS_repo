# file che definisce l'app flask e tutte le sue api web
import json

from flask import Flask, request
from flask_injector import FlaskInjector
from flask_cors import CORS, cross_origin
from injector import inject

from backend.core.core import PREDISCore, DownloadType
from backend.core.dependencies import configure
from backend.core.interfaces.ElectronicAPIInterface import ParamEnum


def create_app():
    ######## INIZIALIZZAZIONE APP #############

    app = Flask(__name__)
    cors = CORS(app)

    @inject
    @app.get('/factory_reset')
    def factory_reset(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        core.factory_reset(devname)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    @inject
    @app.get('/apply_schedule')
    def apply_schedule(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        if core.apply_schedule(devname):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps(
                {'success': False,
                 'msg': f'schedule not applied to {devname}'}
            ), 500, {'ContentType': 'application/json'}
    @inject
    @app.get('/loaded_schedule')
    def loaded_schedule(core: PREDISCore):
        curr_schedule = core.get_loaded_schedule()
        return json.dumps(curr_schedule), 200, {'ContentType': 'application/json'}

    @inject
    @app.get('/shutdown')
    def shutdown(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        if core.shutdown(devname):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps(
                {'success': False,
                 'msg': f'cannot shut down {devname}'}
            ), 500, {'ContentType': 'application/json'}

    @inject
    @app.get("/ping")
    def ping(core: PREDISCore):
        devname = request.args.get('devname')
        force = False
        if 'force' in request.args:
            force = True
        devices = core.ping(devname, force)
        if devices is not None:
            return json.dumps(devices), 200, {'ContentType': 'application/json'}
        return json.dumps(
            {'success': False,
             'msg': f'cannot ping devices'}
        ), 500, {'ContentType': 'application/json'}

    # API per user
    @inject
    @app.get('/devices')
    def get_devices(core: PREDISCore):
        devices = core.get_devices()
        return json.dumps(devices), 200, {'ContentType': 'application/json'}

    @inject
    @app.get('/device')
    def get_device(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        res = core.get_device(devname)
        if res is not None:
            return json.dumps(res), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, 'error': 'device not present'}), 500, {
                'ContentType': 'application/json'}

    @inject
    @app.get('/launch_measure')
    def launch_measure(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        if core.launch_measure(devname):
            return json.dumps({'success': True, }), 200, {
                'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, 'error': "can't launch measure"}), 500, {
                'ContentType': 'application/json'}

    @inject
    @app.get('/download_data')
    def download_data(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        download_type = DownloadType(None, None, None)
        if 'download_type' in request.args:
            download_type.mod = 'new'
            download_type.type = request.args.get('download_type')
        else:
            download_type.mod = 'old'
            download_type.filename = request.args.get('filename')
        if core.download_data(devname, download_type) is not None:
            return json.dumps({'success': True, }), 200, {
                'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, 'error': "can't download data"}), 500, {
                'ContentType': 'application/json'}

    @inject
    @app.get('/set_parameter')
    def set_parameter(core: PREDISCore):
        parameter_map = {
            'THRA': ParamEnum.Thr_A,
            'THRB': ParamEnum.Thr_B,
            'HV': ParamEnum.HV,
            'ACQT': ParamEnum.Acq_Time,
            'PREACQT': ParamEnum.Pre_Acq_Time,
            'CURRT': ParamEnum.Curr_Time,
            'HVSTATE': ParamEnum.HV_State,
            'HVTEMP': ParamEnum.HV_Temp,
            'PULSERSTATE': ParamEnum.Pulser_State,
            'PULSERPERIOD': ParamEnum.Pulser_Period,
            'PULSERWIDTH': ParamEnum.Pulser_Width,
            'CENTRALNODEADDR': ParamEnum.Central_Node_Addr,
        }
        if 'devname' not in request.args or 'parameter' not in request.args or 'val' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'request not valid'}
            ), 500, {'ContentType': 'application/json'}

        devname = request.args.get('devname')
        # download_type può essere conteggi o misure
        parameter_name = request.args.get('parameter')
        param = parameter_map[str(parameter_name).upper()]
        parameter_val = request.args.get('val')
        if core.set_parameter(devname, param, parameter_val):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    @inject
    @app.get('/set_rtc_alarm')
    def set_rtc_alarm(core: PREDISCore):
        if 'devname' not in request.args or 'hour' not in request.args or 'minute' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'request not valid'}
            ), 500, {'ContentType': 'application/json'}

        devname = request.args.get('devname')
        # download_type può essere conteggi o misure
        hour = request.args.get('hour')
        min = request.args.get('minute')

        if core.set_rtc_alarm(devname=devname, hour=hour, minutes=min):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    @inject
    @app.get('/dev_config')
    def get_dev_config(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        res = core.get_dev_config(devname)
        if res is not None:
            return json.dumps(res.to_json()), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    @inject
    @app.get('/update_dev_config')
    def update_dev_config(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        res = core.update_dev_config(devname)
        if res is not None:
            return json.dumps(res.to_json()), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    @inject
    @app.get('/dev_status')
    def get_dev_status(core: PREDISCore):
        if 'devname' not in request.args:
            return json.dumps(
                {'success': False,
                 'msg': 'devname not present'}
            ), 500, {'ContentType': 'application/json'}
        devname = request.args.get('devname')
        res = core.get_dev_status(devname)
        if res is not None:
            return json.dumps(res), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, "error": "device not present"}), 500, {
                'ContentType': 'application/json'}

    # riattivo tutti i dispositivi
    @inject
    @app.get('/turn_on_devices')
    @cross_origin()
    def turn_on_devices(core: PREDISCore):
        if core.turn_on_devices():
            return {'success': True}, 200, {'ContentType': 'application/json'}
        else:
            return {'success': False}, 500, {'ContentType': 'application/json'}

    # API per device

    @inject
    @app.get('/regDev')
    @app.get('/register_device')
    def register_device(core: PREDISCore):
        devname = f"PREDIS{request.args.get('dev')}"
        port = request.args.get('port')
        if core.register_device(devname, request.remote_addr, port):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    @inject
    @app.get('/DwnlLF')
    @app.get('/data_is_ready')
    def data_is_ready(core: PREDISCore):
        if core.data_is_ready(request.remote_addr, request.args['port'] if 'port' in request.args else None):
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

    FlaskInjector(app=app, modules=[configure])
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=1221)
