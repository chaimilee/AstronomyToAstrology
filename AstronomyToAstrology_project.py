import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import sys
import sqlite3

#all the functions that I wrote go here
#make a folder for project-- have script and datasets in there

#code to show the time of querying
from time import gmtime, strftime
import time
#print("\nGMT: "+time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()))

###dataset 1: scraping Astrology.com website###

#print the information of the planet queried
def get_planet_info(planet): 
  content = requests.get('https://www.astrology.com/planets/'+str(planet.strip().lower()))
  soup = BeautifulSoup(content.content, 'html.parser')    
  main=soup('main')   
  for tag in main:
    divs=tag.find_all('div','editorial-article__feed','p')[0]
  return str(divs.get_text())

#static dataset-- save into a json after making into a dictionary
def planet_info_dict():
  planet_list=['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
  planet_dict={}
  for planet in planet_list:
    planet_dict[planet]=str(get_planet_info(planet))
  return planet_dict

#this function converts my dictionaries into jsons. I've used this to create my static dataset
def dict_to_json(file_name, dictionary): #what the file will be called
  with open(filename, "w") as outfile:
    json.dump(dictionary, outfile)


###dataset 2: scraping API of visable planets###

#return the list of planets visable at this location in GMT at the time of querying
def visable_planets(city_name):
  lat_lng_tup=get_latlng_from_df(city_name)
  lat=lat_lng_tup[0]
  long=lat_lng_tup[1]
  response=requests.get('http://visible-planets-api.herokuapp.com/v2?latitude='+str(lat)+'&longitude='+str(long))  
  response=response.json()
  ans_lst=[]
  for planet in response['data']:    
    ans_lst.append(planet['name'])
  return ans_lst

def static_five_cities_to_dict():
  city_lst_top_5=['Los Angeles', 'Tokyo', 'Jakarta', 'Delhi', 'Mumbai']
  five_city_planet_dict={}
  for city in city_lst_top_5:
    five_city_planet_dict[city]=visable_planets(city)
  return five_city_planet_dict


###dataset 3: worldcities.csv dataset###

#return a tuple of lat and lng for most cities (city name as input)
def get_latlng_from_df(city):
  df=pd.read_csv('worldcities.csv')
  for i in range(len(df)):
    if df.at[i, 'city_ascii'].lower()==city.lower():
      lat=df.at[i, 'lat']
      lng=df.at[i, 'lng']
      tup=(lat, lng)
      return tup


#list of top 5 cities for static dataset
city_lst_top_5=['Los Angeles', 'Tokyo', 'Jakarta', 'Delhi', 'Mumbai']

#static sqlite database for planet info
con = sqlite3.connect('final_project.db')
cur = con.cursor()
#create planet_info table from planet_info.json that I created like five_cities.json
cur.execute("DROP TABLE IF EXISTS planet_info")
f=open('planet_info.json')
data=json.load(f)
data_list=data.items()

cur.execute('''CREATE TABLE IF NOT EXISTS planet_info (planet_id TEXT, planet_info TEXT)''')

for line in data_list:

  cur.execute("INSERT INTO planet_info VALUES (?,?)",line)
    
con.commit()


if __name__=='__main__':
    if len(sys.argv)==1:
        print('default')
        print('Please input the name of the city you are located in or would like to know about. Here are some samples you could input: Los Angeles, Seoul, Paris, Kabul')
        user_city=input('Which city are you located in? ')
        #check if the user inputted a city that is in the worldcities.csv dataset
        try:
          user_city_visable_planets=visable_planets(user_city)
        except:
          print('\nCity not available. Please check your spelling or try a different city. You get one more try.')
          user_city=input('Which city are you located in? ')
          user_city_visable_planets=visable_planets(user_city)
        #planets visible in the location of the user
        print('\nYou will feel the effects of these planets: ',user_city_visable_planets,'at',"\nGMT: "+time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime()))
        print('\nI will now be scrapping information about the planets from Astrology.com')

        #if there are more than one planets (which there are most of the time, the code will let you choose which planet to learn about)
        #first time getting info
        if len(user_city_visable_planets)==1:
          user_planet_input=user_city_visable_planets[0]
          print(get_planet_info(user_planet_input))
          print('\nThank you for using my program!')
          sys.exit()
        elif len(user_city_visable_planets)==0:
          print('There are no planets visible in your area')  
          print('\nThank you for using my program!')
          sys.exit() 
        else:
          user_planet_input=input('\nWhich planet would you like to know more about? ')
          while user_planet_input not in user_city_visable_planets:
            print('Choose a valid planet. This planet is either not visible in your area or you mispelled the planet. Note that the first letter has to be uppercased.')
            user_planet_input=input('\nWhich planet would you like to know more about? ')
          print(get_planet_info(user_planet_input))
          user_city_visable_planets.remove(user_planet_input)
          
          #now ask if user wants more info on additional planets  
          more_info=input('Would you like to know more about a different planet? ')

          while more_info.lower()!='yes' and more_info.lower()!='no':
            print('Please answer yes or no')
            more_info=input('\nWould you like to know more about a different planet? ')

          if more_info.lower()=='no':
            print('\nThank you for using my program!')
            sys.exit()

          while more_info.lower()=='yes':
            if len(user_city_visable_planets)==1:
              user_planet_input=user_city_visable_planets[0]
              print(get_planet_info(user_planet_input))
              print('\nThank you for using my program!')
              sys.exit()
            else:
              print('\nOut of ', user_city_visable_planets,',')
              user_planet_input=input('Which planet would you like to know more about? ')
              
              while user_planet_input not in user_city_visable_planets:
                print('\nChoose a valid planet. You have either already learned about this planet or it is not visible in your area. Note that you have to uppercase the first letter in your planet, so please check your spelling!')
                user_planet_input=input('Which planet would you like to know more about? ')
              
              print(get_planet_info(user_planet_input))
              user_city_visable_planets.remove(user_planet_input)
              
              more_info=input('Would you like to know more about a different planet? ')
              
              while more_info.lower()!='yes' and more_info.lower()!='no':
                print('Please answer yes or no')
                more_info=input('\nWould you like to know more about a different planet? ')

              if more_info.lower()=='no':
                print('\nThank you for using my program!')
                sys.exit()
          print('\nThank you for using my program!')
        
    elif sys.argv[1]=='--static': #do a few examples-- save into json print results of few example
        print('static')
        print(len(sys.argv))
        #print('With the static version, I will be running my program with my 3 static datasets: worldcities.csv, five_cities.json, and planet_info.json')
        print('In my static dataset, I have 5 sample cities available: Los Angeles, Tokyo, Jakarta, Delhi, and Mumbai')
        print('I have information on what planets were visible at 5:40 AM 11/25/2021 GMT (the time of querying), stored in a json')
        user_city=input('\nWhich city would you like to know about? ')
        #check if the user inputted a city that is in the list

        while user_city not in city_lst_top_5:
          print('Please choose from the 5 cities given')
          user_city=input('Which city would you like to know about? ')

        print('\nThese are the planets that were visible in ', user_city, ' at 5:40 AM 11/25/2021 GMT (the time of querying)')
        with open('five_cities.json', 'r') as file:
          five_cities_json=json.load(file)
          print(five_cities_json[user_city])

        print('\nNow, I will be using my static dataset on astrological information of planets that I have stored into a sqlite database called final_project.db')
        user_planet_input=input('\nWhich planet would you like to know more about? ')
        while user_planet_input not in five_cities_json[user_city]:
            print('Choose a valid planet. This planet is either not visible in your area or you mispelled the planet. Note that the first letter has to be uppercased.')
            user_planet_input=input('\nWhich planet would you like to know more about? ')

        print('\nI will be pulling static information about planets that I scraped from astrology.com')
        print(cur.execute("SELECT * FROM planet_info WHERE planet_id IS '"+user_planet_input+"'").fetchone()[1])
        five_cities_json[user_city].remove(user_planet_input)

        more_info=input('Would you like to know more about a different planet? ')
        while more_info.lower()!='yes' and more_info.lower()!='no':
          print('Please answer yes or no')
          more_info=input('\nWould you like to know more about a different planet? ')

        if more_info.lower()=='no':
          print('\nThank you for using my program!')
          sys.exit()

        while more_info.lower()=='yes':
          if len(five_cities_json[user_city])==1:
            user_planet_input=five_cities_json[user_city][0]
            print(cur.execute("SELECT * FROM planet_info WHERE planet_id IS '"+user_planet_input+"'").fetchone()[1])
            print('\nThank you for using my program!')
            sys.exit()
          else:
            print('\nOut of ',five_cities_json[user_city],',')
            user_planet_input=input('Which planet would you like to know more about? ')
            while user_planet_input not in five_cities_json[user_city]:
              print('\nChoose a valid planet. You have either already learned about this planet or it is not visible in your area. Note that you have to uppercase the first letter in your planet, so please check your spelling!')
              user_planet_input=input('Which planet would you like to know more about? ')
            print(cur.execute("SELECT * FROM planet_info WHERE planet_id IS '"+user_planet_input+"'").fetchone()[1])
            five_cities_json[user_city].remove(user_planet_input)
              
            more_info=input('Would you like to know more about a different planet? ')
              
            while more_info.lower()!='yes' and more_info.lower()!='no':
              print('Please answer yes or no')
              more_info=input('\nWould you like to know more about a different planet? ')

            if more_info.lower()=='no':
              print('\nThank you for using my program!')
              sys.exit()
        print('\nThank you for using my program!')
        cur.close()
