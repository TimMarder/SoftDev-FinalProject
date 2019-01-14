# Team FiveKnees
### Clara Mohri, Jared Asch, Vincent Lin
### P02: The End

## Description
Event Calendar is a tool that organizes events and allows users to share events with people through email.

## Instructions
1. Clone this repo
```
$ git clone https://github.com/VinnyLin72/SoftDev-FinalProject.git
```

2. Activate your virtual environment
```
$ python3 -m venv venv
$ . venv/bin/activate
```

3. Enter directory
```
$ cd SoftDev-FinalProject
```

4. Install dependencies
```
$ pip install -r requirements.txt
```

5. Procure API keys(instructions [below](https://github.com/VinnyLin72/SoftDev-FinalProject#dependencies))

6. Edit keys.json to add your own keys

7. Run app
```
$ python app.py
```

8. Open your web browser and open `localhost:5000`

9. Use <kbd> CTRL </kbd> + <kbd> C </kbd> to terminate your session

10. Type `deactivate` to deactivate your virtual environment

## Dependencies

1. urllib - used to get JSON files from APIs
2. json - used to parse JSON files
3. flask - allows app to run on 'localhost'
   - imported through pip installing reuirements.txt
4. passlib - used to hash passwords
   - imported through pip installing reuirements.txt
5. flask-mail - used to send emails through app

### APIs

1. Holiday API
   - Sign up [here](https://holidayapi.com/) to recieve a key
   - API responds with a dictionary of holidays and their dates
   - We used this API in our calendar
2. Openstaticmap API
   - Sign up [here](https://developer.mapquest.com/) to recieve a key
   - API shows a map of a chosen area
   - We used this API to display the locations of events
3. Openweathermap API
   - Sign up [here](https://openweathermap.org/api) to recieve a key
   - API tells us the weather for an area by name, coordinates, zip code or city id 
   - We used this API to display the weather at the time and place of the event

