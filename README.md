Launch the Web Application using:

python3 myapp.py

Go to the url mentionned in the console.

Example of curl request to send the empire.json to the web application: 

curl --header "Content-Type: application/json" --request POST --data '{ "countdown": 8,"bounty_hunters": [{ "planet": "Hoth", "day": 6}, { "planet": "Hoth", "day": 7}, { "planet": "Hoth", "day": 8}]}' http://127.0.0.1:5000/

Once sent, refresh the application.
