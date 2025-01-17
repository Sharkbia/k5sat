import head
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import cross_origin
import ephem
import os

app = Flask(__name__)


def local2utc(local_dtm):
    # 本地时间转 UTC 时间（ -8:00 ）
    return datetime.utcfromtimestamp(local_dtm.timestamp())

@app.route("/amateur.txt")
@cross_origin()
def amateur():
    return send_from_directory(os.getcwd(), "amateur.txt")

@app.route("/pass", methods=['POST'])
@cross_origin()
def satpass():
    sat = request.json.get('sat', '')
    sat_line_1 = request.json.get('sat_line_1', '')
    sat_line_2 = request.json.get('sat_line_2', '')
    lat = request.json.get('lat', 0)
    lng = request.json.get('lng', 0)
    alt = request.json.get('alt', 0)

    target_satellite, find_flag = head.FIND_SATE(sat_line_1, sat_line_2, sat)
    pass_times, departure_times = head.CAL_PASS_TIME(target_satellite,
                                                     float(lat), float(lng),
                                                     float(alt))

    return jsonify({
        'code': 200,
        'pass_times': pass_times,
        'departure_times': departure_times
    })


@app.route("/doppler", methods=['POST'])
@cross_origin()
def doppler():
    sat = request.json.get('sat', '')
    sat_line_1 = request.json.get('sat_line_1', '')
    sat_line_2 = request.json.get('sat_line_2', '')
    lat = request.json.get('lat', 0)
    lng = request.json.get('lng', 0)
    alt = request.json.get('alt', 0)
    tx = request.json.get('tx', 0)
    rx = request.json.get('rx', 0)
    format = "%Y-%m-%d %H:%M:%S"
    pass_time = datetime.strptime(request.json.get('pass_time', ''), format)
    departure_time = datetime.strptime(request.json.get('departure_time', ''),
                                       format)
    satellite = ephem.readtle(sat, sat_line_1, sat_line_2)
    # print(str(pass_time) + " " + str(local2utc(pass_time)))
    shift_array = []
    while pass_time < departure_time + timedelta(seconds=1):
        AZ, EI, SHITF_UP, SHIFT_DOWN, DIS = head.CAL_DATA(
            satellite, sat_line_1, sat_line_2, float(lng), float(lat),
            float(alt), local2utc(pass_time),
            float(tx) * 1000000,
            float(rx) * 1000000)
        shift_array.append([SHITF_UP, SHIFT_DOWN])
        pass_time = pass_time + timedelta(seconds=1)
    return jsonify({'code': 200, 'shift_array': shift_array})
