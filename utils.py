# import smbus
from smbus2 import SMBus
import time
import requests
import subprocess
import aiohttp
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
bus = SMBus(1) # Rev 2 Pi uses 1
# time.sleep(1)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)
  # time.sleep(1)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def get_datetime():
  now = time.strftime('%H:%M:%S  %b %d')
  t =time.localtime()
  minute = t.tm_min
  sec = t.tm_sec
  return now,minute,sec

def get_location_old():
    LOCATION = None
    url = "http://ipinfo.io/loc"
    try:
      a = requests.get(url)
      if a.status_code == 200:
          a = a.text
          a = a.replace("\n","")
          a = a.split(",")
          k = ['lat','lon']
          LOCATION = dict(zip(k,a))
          print(LOCATION)
    except:
      pass
    return LOCATION

async def get_location():
    LOCATION = None
    
    try:
      req_url = "http://ipinfo.io/loc"
      # a = requests.get(url)
      async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(req_url) as response:
          if response.status == 200:
              a = await response.text()
              print("a is ::",a)
              a = a.replace("\n","")
              a = a.split(",")
              k = ['lat','lon']
              LOCATION = dict(zip(k,a))
              print(LOCATION)
    except Exception as e:
      print("Exception in get_location()")
      print(e)
    return LOCATION

def get_weather_openweathermap_old(api_key,lat,lon,city=None):
    res = "No Weather data"
    try:
      if city is None:
          req_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
          # req_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
          response = requests.get(req_url)
          if response.status_code == 200:
              response = response.json()
              temp_main = round(response["main"]["feels_like"])
              weather_main = response["weather"][0]["main"]
              res = f"{temp_main}ßC {weather_main}"[:16]
              # print(res)
    except Exception as e:
      print("Exception in get weather old",e)
    return res

async def get_weather_openweathermap(api_key,lat,lon,city=None):
    res = "No Weather data"
    try:
      if city is None:
          req_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
          # response = await requests.get(req_url)
          async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(req_url) as response:
              if response.status == 200:
                  response = await response.json()
                  temp_main = round(response["main"]["feels_like"])
                  weather_main = response["weather"][0]["main"]
                  res = f"{temp_main}ßC {weather_main}"[:16]
                  # print(res)
    except Exception as e:
      print(e)
    return res
def get_weather_weathercom(api_key,lat,lon,city=None):
    res = "No Weather data"
    try:
      if city is None:
          # req_url = f"https://api.weather.com/v2/turbo/vt1observation?apiKey={api_key}&format=json&geocode={lat}%2C{lon}&language=en-IN&units=m"
          req_url = f"https://api.weather.com/v3/wx/observations/current?geocode={lat}%2C{lon}&units=m&language=en-IN&format=json&apiKey={api_key}"
          response = requests.get(req_url)
          if response.status_code == 200:
              response = response.json()
              temp_main = int(response["temperatureFeelsLike"])
              weather_phrase = response["wxPhraseLong"]
              res = f"{temp_main}ßC  {weather_phrase}"[:16]
              print(res)
    except:
      pass
    return res