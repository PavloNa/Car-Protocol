# UDPPingerServer.py
from email import message
from inspect import CO_VARKEYWORDS
import io
import sys
import random
from socket import *
from turtle import distance
import time
import numpy as np
from threading import Thread
import geopy.distance
import rsa

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 12000))
recieved = b"Recieved."
global carArray
carArray = {}
global carSpeed
carSpeed = {}
global connect
connect = False
global carKey
carKey = {}
global publicKey, privateKey
publicKey, privateKey = rsa.newkeys(512)

def checksum(message):
	Sum = sum(bytearray(bytes(message[0], encoding='utf-8')))
	for i in range(1, len(message) - 1):
		Sum += sum(bytearray(bytes(message[i], encoding='utf-8')))
	Sum += 33 * (len(message) - 1)
	return Sum

def tuppleError(msg):
    msg = msg.replace("(", "")
    msg = msg.replace(")", "")
    msg = msg.replace("'", "")
    msg = msg.replace(" ", "")
    msg = msg.split(",")
    tuplefinal = (msg[0], int(msg[1]))
    return tuple(tuplefinal)

def getCoords(coords):
    coords = coords.split(",")
    x = float(coords[0])
    y = float(coords[1])
    cor = (x, y)
    return cor

def AddCars(c_address, separated): #Function responsible for adding cars and updating their speeds
    loc = str(separated[2]) + "," + str(separated[3])
    carArray = {c_address : str(loc)} #Car/Location
    return carArray

def newCar():
	global carArray
	global carSpeed
	global connect
	global publicKey
	global carKey
	while True:
		try:
			connect = False
			print("Waiting for requests...")
			time.sleep(3)
			data1 = serverSocket.recvfrom(1024) #Recieve new car
			c_message =  data1[0].decode("utf-8")
			c_address = data1[1]
			separated = c_message.split("!") #Separate array
			if separated[0] == "5":
				serverSocket.sendto(bytes(str(publicKey), encoding = 'utf-8'), c_address)
				if len(carKey) == 0:
					carKey = {c_address: separated[1]}
				else:
					carKey[c_address] = str(separated[1])
			else:
				#print(carKey)
				#print(separated)
				#print(c_message) Debugging
				if separated[0] == str(0):
					check = separated[6]
				elif separated[0] == str(1):
					check = separated[3]
				elif separated[0] == str(3):
					check = separated[2]
				else:
					check = 0
		
				if separated[0] == str(0):
					auth = separated[5]
				elif separated[0] == str(1):
					auth = separated[2]
				elif separated[0] == str(3):
					auth = separated[1]
				else:
					check = 0
				#print(check)   #DEBUGGING
				if auth == "Gd+CsYxn8_PE":
					print("Authenticated successfuly!")
					if int(checksum(separated)) == int(check):
						if separated[0] == str(0):
							print("Car attempting conncetion: " + str(separated))           
						elif separated[0] == str(1):
							print("Updating speed of " + str(c_address))
						else:
							print("Attempting deletion")
						if str(separated[0]) == "0": #IF NEW CAR
							if str(separated[1]) == "1": #IF CAR IS ON
								if len(carArray) == 0:
									carArray = AddCars(c_address, separated)
									carSpeed = {c_address : separated[4]}
								else:
									carArray[c_address] = str(separated[2])+ "," + str(separated[3])
									carSpeed[c_address]= separated[4]
							else: #IF CAR OFF
								if c_address in carArray:
									carArray.pop(c_address) #GET RID OF CAR
									carSpeed.pop(c_address) #GET RID OF SPEED REGISTER
								else:
									print("Non-existent car, request ignored.")
						if str(separated[0]) == "1": #IF UPDATE SPEED CODE
							carSpeed[c_address] = separated[1] #UPDATE SPEED
						if str(separated[0]) == "4":
							carArray[c_address] = str(separated[2])+ "," + str(separated[3])
						if str(separated[0]) == "3":
							carArray.pop(c_address) #GET RID OF CAR
							carSpeed.pop(c_address)
							connect = True
						#print(carArray)   	                                           #Debugging pursposes ----------||--------
						#print(carSpeed)                                               #Debugging pursposes ----------||--------
					else:
						err = b'2'
						serverSocket.sendto(err, c_address)
				else:
					print("Incorrect authentication")
					pass
		except ConnectionResetError:
			print("timeout")
			connect = True
			if c_address in carArray:
				carArray.pop(c_address)
				carSpeed.pop(c_address)
			print(carSpeed)
			print(carArray)
 


 #OTHER FUNCTIONS
def sendLoc():
	global carSpeed
	global carArray
	global connect
	while True:
		if connect == True:
			break
		if len(carArray) == 0 & len(carArray) == 1:
			time.sleep(5)
		else:
				for key in list(carArray):
					for key2 in list(carArray):
						if key == key2:
							continue
						else:
							try:
								testmessage = b'Conectivity check'
								serverSocket.sendto(testmessage, tuppleError(str(key2)))
							except:
								carArray.pop(key2) #GET RID OF CAR
								carSpeed.pop(key2) #GET RID OF SPEED REGISTER
								continue
							if carArray.get(key2) == None or carArray.get(key) == None:
								continue
							else:
								coords_1 = getCoords(str(carArray.get(key2)))
								coords_2 = getCoords(str(carArray.get(key)))
								Distance = geopy.distance.geodesic(coords_1, coords_2).miles
								if Distance <= 10:
									message = 'Car info: ' + str(key2) + ' Distance: ' + str(Distance) + ' Location: ' + str(carArray.get(key2)) + " Speed: " + str(carSpeed.get(key2))
									message = bytes(message, encoding='utf-8')
									message2 = 'Car info: ' + str(key) + ' Distance: ' + str(Distance) + ' Location: ' + str(carArray.get(key)) + " Speed: " + str(carSpeed.get(key))
									message2 = bytes(message2, encoding='utf-8')
									serverSocket.sendto(message, tuppleError(str(key))) #Send information to car 1
									serverSocket.sendto(message2, tuppleError(str(key2))) #Send information to car 2
				time.sleep(5)
				
    
    
    
if __name__ == '__main__':
    Thread(target = sendLoc).start()
    Thread(target = newCar).start()
#TODO  update location code #ENCRYPT/DECRYPT METHOD 