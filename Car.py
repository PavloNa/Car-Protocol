# @Author: pn00289 (Pavlo Nazarchuk) @University of Surrey project @Computer Networking Coursework
# Theoretical car location exchange server for more precise AI predictions.
# UDPPingerClient.py
# We will need the following module to generate randomized lost packets
# GEOPY IS NECESSARY (pip install geopy)  
import sys
import socket
import time
import random
import geocoder #(PIP INSTALL GEOCODER)
from threading import Thread
import rsa

# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 12000
UDP_SEND = ("127.0.0.1", 12000)
Message = None
Status = b"1"
# create a socket with a 1s timeout.
clientSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
clientSock.connect((UDP_IP_ADDRESS, UDP_PORT_NO))
clientSock.settimeout(600)

#key = clientSock.recvfrom(1024)
#clientSock.sendto(bytes(""), UDP_SEND)
def checksum(message):
    Sum = str(sum(bytearray(message.encode('utf-8'))))
    return Sum

def resend(Message):
    sent=clientSock.sendto(Message, UDP_SEND)
    data = clientSock.recvfrom(1024)
    if data[0].decode("utf-8") == "2":
        resend(Message)

def filterLoc(location):
    location = str(location).replace("[", "")
    location = location.replace("]", "")
    location = location.replace(",", "")
    location = location.replace(" ", "!")
    return location

def messageCreation():
    Message = "0!" #Code for new car
    print("Is you car on?")
    print("0 - No")
    print("1 - Yes")
    choise = int(input("Choose a number:"))
    if choise == 1:
        Message += str("1")
    else:
        Message += str("0")
    
    g = geocoder.ip('me') #LOCATION REQUEST
    print(filterLoc(g.latlng)) 
    Message += "!" + str(filterLoc(g.latlng))
    #Speed will be randomly generated for simplicity
    Speed = random.randint(0,70)
    Message += "!" + str(Speed)
    Message += "!Gd+CsYxn8_PE"
    Message += "!"
    Message += checksum(Message)
    Message = bytes(Message, encoding='ascii')
    print(Message)
    return Message
    
def updateSpeed():
    while True:
        time.sleep(6)
        Message = "1!"
        Speed = random.randint(0,70)
        Message += str(Speed)
        Message += "!Gd+CsYxn8_PE"
        Message += "!"
        Message += checksum(Message)
        Message = bytes(Message, encoding='utf-8')
        clientSock.sendto(Message, UDP_SEND)
    
def carConnection():
    Keyrequest = b'5'
    clientSock.sendto(Keyrequest, UDP_SEND)
    key = clientSock.recvfrom(1024)
    key = key[0].decode('utf-8')
    print(key)
    Message = messageCreation()
    resend(Message)

g = geocoder.ip('me')
print(g.latlng)

carConnection()

def recieve():
    while True:
        try:
            ## sent the Message using the clientSock
            # Receive response
            global stop_threads
            ##get the response & extract data
            data = clientSock.recvfrom(1024)
            if data[0].decode("utf-8") != 'Conectivity check':
                print ('waiting to receive')
                print ('received "%s"' % str(data))
            time.sleep(3)
            if stop_threads:
                break
        except socket.timeout as inst:
            ## handle timeouts
            print('closing socket')

def close():
    while True:
        global stop_threads
        stop_threads = False
        print("If you wish to end the connection enter \"P\"")
        closeval = input()
        if closeval == "P":
            message = '3'
            message += "!Gd+CsYxn8_PE"
            message += "!"
            message += checksum(message)
            clientSock.sendto(bytes(message, encoding='utf-8'), UDP_SEND)
        stop_threads = True
        break
    clientSock.timeout


if __name__ == '__main__':
    Thread(target = recieve).start()
    Thread(target = close).start()
    Thread(target = updateSpeed).start()
    
##TODO ENCRYPT/DECRYPT METHOD, update location thread

