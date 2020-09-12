import pylab
from flask import Flask, jsonify, escape, request
import requests as http_request

# kalman algorithm params
x = 0
p = 0.5
r = 0.4
cycle = 0
lastMsg = 0

angle = []
angle_filter = []

# command url
command_url = 'http://127.0.0.1:48082/api/v1/device/a7754a90-599f-47ac-a8a6-209505dd7220/command/d57fc15c-87af-4c5d-91f7-0c85a4c6f813'
# statistic url
statistic_url = 'http://192.168.1.101:7777/'

# device mode
device_mode = True

# *****************************************
# setup App
# *****************************************
app = Flask(__name__)
# jsonify configure Chinese normal display
app.config["JSON_AS_ASCII"] = False


# *****************************************
# defined kalman algorithm
# *****************************************
def kalman(new_measure):
    global x
    global p
    global r
    k = p / (p + r)
    p = (1 - k) * p
    x = x + k * (new_measure - x)
    return x


# *****************************************
# draw feature with measurement/estimation
# *****************************************
def plotfig(a, b):
    pylab.figure().clf()
    pylab.figure()
    pylab.plot(a, 'k*', label='measurement')
    pylab.plot(b, 'b^', label='estimation')
    pylab.title('Angle of the wind')
    pylab.legend()
    pylab.xlabel('time')
    pylab.ylabel('angle')
    pylab.show()


# *****************************************
# data process function
# *****************************************
def data_process(new_value):
    # initialize x
    global cycle
    global x
    global p
    global lastMsg

    if cycle == 0:
        x = new_value
    cycle += 1

    if abs(new_value - lastMsg) > 10:
        x = new_value
        p = 0.5
    lastMsg = new_value

    result = int(kalman(new_value))
    angle.append(new_value)
    angle_filter.append(result)
    # draw feature
    if len(angle_filter) % 100 == 0:
        plotfig(angle, angle_filter)
    # plotfig(angle, angle_filter)
    return result


# *****************************************
# send command to device
# *****************************************
def send_command(content):
    global command_url
    global statistic_url
    request_params = {
        'message': str(content)
    }
    headers = {
        'content-type': 'application/json'
    }
    http_request.get(statistic_url, request_params)
    # send command request
    r = http_request.put(command_url, json=request_params, headers=headers)
    print(r.text)


'''
description:
    welcome message
'''


@app.route('/')
def welcome():
    name = request.args.get("name", "World")
    return f'Welcome to data analysis service, {escape(name)}!'


'''
description:
    collect data for analysis
methods:
    ['POST']
requestBody:
    EdgeX Foundry event data
    eg: {
        "id": "cdsdf-sdkbe-sdsds-sdsds-jidef",
        "device": "MQ_DEVICE",
        "origin": 1599308375787,
        "readings": [{
            "id": "cdsdf-sdkbe-sdsds-sdsds-jidef",
            "origin": 1599308375787,
            "device": "MQ_DEVICE",
            "name": "randnum",
            "value": 123.223
        }]
    }
'''


@app.route('/analysis/dataCollect', methods=['POST'])
def data_collect():
    global angle_filter
    # get data from request body
    request_json = request.json
    # data form request string
    new_data = request_json.get('readings')[0].get('value')
    print("====================================")
    print("Get data from device " + new_data)
    # last result of kalman algorithm
    last_result = angle_filter[len(angle_filter) - 1] if len(angle_filter) else 0
    # analysis result by kalman algorithm
    analysis_result = data_process(int(new_data))
    # determine whether to send command to device
    if last_result != analysis_result:
        send_command(analysis_result)
        print("After Kalman, send target " + str(analysis_result))
        print("====================================")
        return jsonify({"code": 200, "message": "command send successfully!"})

    return jsonify({"code": 200, "message": "data collect successfully!！"})


@app.route('/analysis/changeMode', methods=['POST'])
def change_mode():
    global device_mode
    print(device_mode)
    # get data from request body
    request_json = request.json
    # get new state
    device_mode = request_json.get('state')

    return jsonify({"code": 200, "message": "success"})


def main():
    app.run(host='0.0.0.0', port=7777)


if __name__ == '__main__':
    main()
