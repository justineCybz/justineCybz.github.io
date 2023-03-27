#!/bin/python3
import requests

username = "natas2"
password = "h4ubbcXrWqsTo7GGnnUMLppXbOogfBZ7"

r = requests.get('http://natas2.natas.labs.overthewire.org/files/users.txt', auth=(username, password))
print(r.content.decode('UTF-8'))
