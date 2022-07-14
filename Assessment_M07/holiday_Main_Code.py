from datetime import datetime
import json
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from config import jsonHolidayloc
from config import savedHolidayloc
from config import menutxtloc


f = open("menu.txt")
menutxt = f.read()
# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
class Holiday:
    
    """Holiday"""     
    
    def __init__(self, name, date):
        self._name = name
        self._date = datetime.strptime(date,"%Y-%m-%d")
    
    #Get
    @property
    def name(self):
        return self._name

    @property
    def date(self):
        return self._date

    #Set
    @name.setter
    def name(self, new_name):
        self._name = new_name

    @date.setter
    def date(self, new_date):
        self._date = new_date
    
    def __str__ (self):
        # String output
        # Holiday output when printed.
        HolidayOutput = (f"{self._name} ({self._date.strftime('%Y-%m-%d')})")
        return HolidayOutput
    
    def DateChange(self):
        # to turn this element into a dictionary, date needs to be formatted as a string
        dateDict = {}
        dateDict['name'] = self._name
        dateDict['date'] = self._date.strftime('%Y-%m-%d')
        return dateDict
                  
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
class HolidayList:
    def __init__(self):
       self.innerHolidays = []
   
    def addHoliday(self, holidayObj):
        # Make sure holidayObj is an Holiday Object by checking the type
        if (type(holidayObj)== Holiday):
        # Use innerHolidays.append(holidayObj) to add holiday
        # print to the user that you added a holiday
            self.innerHolidays.append(holidayObj)
            print(f"Success: You have added {holidayObj} to the list of holidays!")
        else:
            print("Sorry, what you entered was not a Holiday object!")

    def findHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays
        for holiday in self.innerHolidays:
            if holiday.name == HolidayName and holiday.date == Date:
                return holiday
        # Return Holiday

    def removeHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays by searching the name and date combination.
        # remove the Holiday from innerHolidays
        # inform user you deleted the holiday
        numberDeleted = 0
        for i in range(len(self.innerHolidays)):
            holiday = self.innerHolidays[i]
            if (holiday.name == HolidayName and holiday.date == Date):
                print(f"Success:{HolidayName} has been deleted from the list!")
                del self.innerHolidays[i]
                numberDeleted += 1
        if numberDeleted == 0:
            print(f"Sorry! {HolidayName} was not found!")

    def readMenuTxtFile():
        global menutxt
        f = open(menutxtloc, 'r') 
        menutxt = f.read()

    def read_json(self, filelocation):
        # Read in things from json file location
        # Use addHoliday function to add holidays to inner list.
        with open(filelocation, 'r') as file:
            holidayData = json.load(file)['holidays']

        for i in range(len(holidayData)):
            name = holidayData[i]['name']
            date = holidayData[i]['date']
            holiday = Holiday(name, date)
            self.addHoliday(holiday)

    def save_to_json(self, filelocation):
        # Write out json file to selected file.
        listHolidayDictionaries = list(map(lambda x: x.DateChange(), self.innerHolidays))
        fullOutputDictionary = {'holidays': listHolidayDictionaries}
        JSONFormatting = json.dumps(fullOutputDictionary, indent=2)
        #Now writing to file
        with open(filelocation, "w") as file:
            file.write(JSONFormatting)
        
    def scrapeHolidays(self):
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        # Remember, 2 previous years, current year, and 2  years into the future. You can scrape multiple years by adding year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        # Check to see if name and date of holiday is in innerHolidays array
        # Add non-duplicates to innerHolidays
        # Handle any exceptions.
        try:
            holidays = []
            #going from 2 years in the past to two years in the future
            for year in range(2020,2025):

                url = (f'https://www.timeanddate.com/holidays/us/{year}?hol=33554809')
                connection = requests.get(url).text

                soup = BeautifulSoup(connection, 'html.parser')
                table = soup.find('table', attrs={'id':'holidays-table'})
                body = table.find('tbody')
                #Finding all 
                for row in body.find_all('tr'):
                    
                    #Holiday Dictionary
                    HolidayDict = {}

                    date = row.find('th')
                    Holname = row.find('a')

                    #check rows where date and name are not None
                    if date is not None and Holname is not None:
                        
                        #format date correctly
                        date = date.text
                        date = f"{date} {year}"
                        date= datetime.strptime(date,"%b %d %Y")
                        # date = date.date()
                        date = date.strftime('%Y-%m-%d')
                        
                        HolidayDict['Name'] = Holname.text
                        HolidayDict['Date'] = date
                    
                    holidays.append(HolidayDict)

                    #remove empty dictionaries from list
                    while {} in holidays:
                        holidays.remove({}) 

                    #remove duplicate holidays
                    holidays = [dict(t) for t in {tuple(d.items()) for d in holidays}]

            
            for i in holidays:

                temphol = (Holiday(i['Name'], i['Date']))
                #adding in non duplicate holidays to the inner holiday class
                if temphol not in self.innerHolidays:
                    self.innerHolidays.append(temphol)
                
        except:
                print("Sorry there was a connection issue!")

    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        HolidayNumber = len(self.innerHolidays)
        return HolidayNumber
    
    def filter_holidays_by_week(self, year, week_number):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        # Week number is part of the the Datetime object
        # Cast filter results as list
        #Filter by year
        yearFilter = list(filter(lambda a: (a.date.year == year), self.innerHolidays))
        #Filter by week after filtering by year
        HolidaysbyWeek = list(filter(lambda a: (a.date.isocalendar()[1] == week_number), yearFilter))
        # return your holidays
        return HolidaysbyWeek


    def displayHolidaysInWeek(self, holidayList):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        # Output formated holidays in the week. 
        # * Remember to use the holiday __str__ method.
        for holiday in holidayList: 
            print(holiday)

    #def getWeather(weekNum):
    #unable to get this to work!
        # Convert weekNum to range between two days
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.

    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        currentYear = datetime.now().year
        currentWeek = datetime.now().isocalendar()[1]
        # Use your filter_holidays_by_week function to get the list of holidays 
        # for the current week/year
        weekHolidays = self.filter_holidays_by_week(currentYear, currentWeek)
        # Use your displayHolidaysInWeek function to display the holidays in the week
        self.displayHolidaysInWeek(weekHolidays)
        # Ask user if they want to get the weather
        # If yes, use your getWeather function and display results



def main():
    # Large Pseudo Code steps
    # -------------------------------------
    # 1. Initialize HolidayList Object
    global jsonHolidayloc
    global menutxt
    List = HolidayList()
    # 2. Load JSON file via HolidayList read_json function
    List.read_json(jsonHolidayloc)
    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    List.scrapeHolidays()
    HolidayCount = List.numHolidays()
    print("Holiday Management")
    print("===================")
    print(f"There are {HolidayCount} holidays store in the system.")
    # 3. Create while loop for user to keep adding or working with the Calender
    notDone = True
    saved = True
    while notDone:
        try:
            # 4. Display User Menu (Print the menu)
            print(menutxt)
            UserChoice = int(input("What would you like to do? ")) 
            if (UserChoice == 1):
                #add holiday
                print("Add a Holiday")
                print("=============")
                NewHoliday = str(input("Holiday: "))
                validDate = False
                while not validDate:
                    NewDate = str(input("Date: "))
                    #See if date can be converted to datetime format, if not then it is not correct
                    try:
                        datetime.strptime(NewDate, "%Y-%m-%d")
                        validDate = True
                    except:
                        print("That is an incorrect date format. Please use the YYYY-MM-DD format!")
                holiday = Holiday(NewHoliday, NewDate)
                List.addHoliday(holiday)
                saved = False
                print("Back to the main menu!")
            elif (UserChoice == 2):
                #Remove holiday
                print("Remove a Holiday")
                print("================")
                ExHoliday = str(input("Holiday: "))
                validDate = False
                while not validDate:
                    ExDate = str(input("Date: "))
                    #See if date can be converted to datetime format, if not then it is not correct
                    try:
                        datetime.strptime(ExDate, "%Y-%m-%d")
                        validDate = True
                    except:
                        print("That is an incorrect date format. Please use the YYYY-MM-DD format!")
                ExDate = datetime.strptime(ExDate, "%Y-%m-%d")
                IsListed = List.findHoliday(ExHoliday, ExDate)
                if (IsListed != None):
                    #remove holiday
                    List.removeHoliday(ExHoliday, ExDate)
                    saved = False
                else:
                    print("That holiday is not in the system!")
                print("Back to the main menu!")
            elif (UserChoice == 3):
                #Save Holiday LIst
                print("Saving Holiday List")
                print("===================")
                validChoice = False
                while not validChoice:
                    Saving = input("Are you sure you want to save your changes? [y/n]: ")
                    #answer is yes, save data
                    if (Saving.lower().strip() == "y"):
                        print("Success: Your changes have been saved.")
                        List.save_to_json(savedHolidayloc)
                        saved = True
                        validChoice = True
                    elif (Saving.lower().strip() == "n"):
                        print("Canceled: Holiday list file save canceled.")
                        validChoice = True
                    else: 
                        print("Invalid Entry")  
                        validChoice = False   

            elif (UserChoice == 4):
                #View Holidays
                print("View Holidays")
                print("=============")
                validYear = False
                while not validYear:
                    pickedYear = int(input("Which Year?: "))
                    if pickedYear >= 2020 and pickedYear <= 2025:
                        validYear = True
                    else:
                        print("Sorry that is not a valid year. Please pick between 2020 and 2025")
                validWeek = False
                while not validWeek:
                    pickedWeek = int(input("Which week?: #[1-52, Leave blank for the current week]:"))
                    if pickedWeek >= 1 and pickedWeek <= 52 or pickedWeek == "":
                        validWeek = True
                    else:
                        print("Sorry that is not a valid week. Please pick between 1 and 52")
                if (pickedWeek == ""):
                    print("These are the holidays for this week:")
                    List.viewCurrentWeek()
                else:
                    print("The holidays for this selected week are: ")
                    List.displayHolidaysInWeek(List.filter_holidays_by_week(pickedYear, pickedWeek))

            elif (UserChoice == 5):
                #Exit
                print("Exit")
                print("====")
                validChoice = False
                while not validChoice:
                    if (saved == True):
                        leaving = input("Are you sure you want to exit? [y/n]: ")
                        if (leaving.lower().strip() == "y"):
                            print("Goodbye!")
                            notDone = False
                            validChoice = True
                        if (leaving.lower().strip() == "n"):
                            print("You will be redirected back to the main menu!") 
                            validChoice = True   
                    if (saved == False):
                        leaving = input("Are you sure you want to exit?\n Your changes will be lost.\n [y/n]: ") 
                        if (leaving.lower().strip() == "y"):
                            print("Goodbye!")
                            notDone = False
                            validChoice = True
                        if (leaving.lower().strip() == "n"):
                            print("You will be redirected back to the main menu!") 
                            validChoice = True
            else:
                print("Sorry! That is not a valid choice. You will be returned to the main menu")
                notDone = True
        except:
            print("Sorry that is not a valid entry.")
    # 5. Take user input for their action based on Menu and check the user input for errors
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 


if __name__ == "__main__":
    main()


# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.





