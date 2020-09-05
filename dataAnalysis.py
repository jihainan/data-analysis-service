import paho.mqtt.client as mqtt
import os
import random
import pylab


HOST = "192.168.31.142"
PORT = 1883
x= 0
p=0.5
r=0.4
cycle=0
lastMsg=0


angle=[]
angle_filter=[]


def kalman(newMeasure):
    global x
    global p
    global r
    k= p/(p+r)
    p=(1-k)*p
    x= x+ k*(newMeasure-x)
    return x

def plotfig(a,b):
    pylab.figure()
    pylab.plot(a,'k*',label='measurement')
    pylab.plot(b,'b^',label='estimation')
    pylab.title('Angle of the wind')
    pylab.legend()
    pylab.xlabel('time')
    pylab.ylabel('angle')
    pylab.show()


def on_message_callback(client, userdata, message):

    msg= str(message.payload)
    msg= msg[2:-1]


    # send DataTopic---one angle
    if msg.isdigit():

        print("====================================")
        print("Get data "+msg)

        #initialize x
        global cycle
        global x
        global p
        global lastMsg

        if cycle==0:
            x=int(msg)
        cycle+=1

        if abs(int(msg)-lastMsg)>10:
            x= int(msg)
            p= 0.5
        lastMsg=int(msg)


        result= int(kalman(int(msg)))
        angle.append(int(msg))
        angle_filter.append(result)
        if len(angle_filter)==100:
            plotfig(angle,angle_filter)

        command = "mosquitto_pub -h 192.168.31.142 -t YanniTopic  -m "+ str(result)+str(result)
        print("After Kalman, send terminal "+ str(result))
        print("====================================")
        print("")
        os.system(command)



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("YanniiTopic")


def main():
    client = mqtt.Client('test')
    client.connect(HOST, PORT, 60)
    client.on_connect = on_connect
    client.on_message = on_message_callback
    client.loop_forever()


if __name__ == '__main__':
    main()


