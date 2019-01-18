# Team FiveKnees
### Clara Mohri, Jared Asch, Vincent Lin
### P02: The End


## Brief Description

EventCalendar is a tool that organizes events and allows users to share events with people through email.  
Holidays can be viewed, users can create events, and users can maintain an address book with their contacts.  
When viewing events, location and forecast are displayed with the events for which this data is available.
Inviting others to events with accounts allows them to accept the event and add to their own event list.


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

4. Install [dependencies](https://github.com/VinnyLin72/SoftDev-FinalProject#apis)
```
$ pip install -r requirements.txt
```

5. Procure API keys(instructions [below](https://github.com/VinnyLin72/SoftDev-FinalProject#dependencies))

6. Edit [keys.json](https://github.com/VinnyLin72/SoftDev-FinalProject/blob/master/data/keys.json) to add your own keys
```
{
    "MAPQUEST_KEY": "[OPEN_STATIC_MAP_API_KEY]",
    "OPEN_WEATHER_MAP_KEY": "[OPEN_WEATHER_MAP_API_KEY]",
    "HOLIDAY_KEY": "[CALENDAR_INDEX_API_KEY]"
}
```

7. Run app
```
$ python app.py
```

8. Open your web browser and open `localhost:5000`
   - App instructions [below](https://github.com/VinnyLin72/SoftDev-FinalProject#how-to-use)

9. Use <kbd> CTRL </kbd> + <kbd> C </kbd> to terminate your session

10. Type `deactivate` to deactivate your virtual environment



## How To Use:

1. Start by creating an account. Make sure your password is more than five characters long.
2. Once your account has been created, you can log in. You'll see a list of holidays for the current year.

### To Create an Event:

1. Click the "Create Event" button. You will be led to a form to create an event. 
2. Fill out this form. If you input a location, make sure that the address is complete. This way, when viewing your events, you will be able to see the location on a map, as well as the forecast for the event once this data becomes available.
3. If you have contacts in your Address Book, when you invite people you'll have autofill. Inviting people will send them an email with a description of the event.
3. If those you have invited have/create an account, they will be able to accept/decline the invite on their own event lists.

### To Add Contacts

1. Click the "Address Book" button in the upper right hand corner. Here, you'll be able to view your contacts.
2. Click the "Add contacts" button. You'll be led to a form to create an event. 
3. If you add a birthday for your contact, then the birthday will appear in your events list. 

### To Edit an Event:

1. Go to your events list on the landing page. 
2. On the event that you'd like to edit, click the three small dots, and select "edit."
3. You'll be  led to a form where you can edit your event.
4. If you change the invited people, the emails on the new input will be emailed that they have been invited to an event that you have updated.

### To Delete an Event: 

1. Go to your events list on the landing page. 
2. On the event that you'd like to delete, click the three small dots, and select "delete."


## Dependencies

1. urllib - used to get JSON files from APIs
2. json - used to parse JSON files
3. flask - allows app to run on 'localhost'
   - imported through pip installing requirements.txt
4. passlib - used to hash passwords
   - imported through pip installing requirements.txt
5. flask-mail - used to send emails through app
   - imported through pip installing requirements.txt

### APIs

1. CalendarIndex API
   - Sign up [here](https://www.calendarindex.com/signup) to receive a key 
      - Note: It takes a bit of time to receive key from them
   - API responds with a dictionary of holidays and their dates
   - We used this API for holiday events
2. Openstaticmap API
   - Sign up [here](https://developer.mapquest.com/) to receive a key
   - API shows a map of a chosen area
   - We used this API to display the locations of events
3. Openweathermap API
   - Sign up [here](https://openweathermap.org/api) to receive a key
   - API tells us the weather for an area by name, coordinates, zip code or city id 
   - We used this API to display the weather at the time and place of the event

