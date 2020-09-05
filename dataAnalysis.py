import os
import random
import pylab
from flask import Flask, escape, request

# MQTT broker 地址
HOST = "192.168.31.142"
PORT = 1883
x = 0
p = 0.5
r = 0.4
cycle = 0
lastMsg = 0

angle = []
angle_filter = []

# *****************************************
# setup App
# *****************************************
app = Flask(__name__)


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
    pylab.figure()
    pylab.plot(a, 'k*', label='measurement')
    pylab.plot(b, 'b^', label='estimation')
    pylab.title('Angle of the wind')
    pylab.legend()
    pylab.xlabel('time')
    pylab.ylabel('angle')
    pylab.show()


# *****************************************
# MQTT message callback for receive measurement data
# *****************************************
def on_message_callback(client, userdata, message):
    msg = str(message.payload)
    msg = msg[2:-1]

    # send DataTopic---one angle
    if msg.isdigit():

        print("====================================")
        print("Get data " + msg)

        # initialize x
        global cycle
        global x
        global p
        global lastMsg

        if cycle == 0:
            x = int(msg)
        cycle += 1

        if abs(int(msg) - lastMsg) > 10:
            x = int(msg)
            p = 0.5
        lastMsg = int(msg)

        result = int(kalman(int(msg)))
        angle.append(int(msg))
        angle_filter.append(result)
        if len(angle_filter) == 100:
            plotfig(angle, angle_filter)
        # publish message to specific topic
        command = "mosquitto_pub -h 192.168.31.142 -t YanniTopic  -m " + str(result) + str(result)
        print("After Kalman, send terminal " + str(result))
        print("====================================")
        print("")
        os.system(command)


# *****************************************
# connected to MQTT broker
# *****************************************
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("YanniiTopic")


'''
description:
    welcome message
'''


@app.route('/')
def welcome():
    name = request.args.get("name", "World")
    return f'Welcome to data analysis service, {escape(name)}!'


def main():
    app.run(host='0.0.0.0', port=7777)


if __name__ == '__main__':
    main()
