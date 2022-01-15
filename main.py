import time
import os
from time import sleep
# from utilss import utils
import utils
import subprocess
import asyncio

LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

def display_ip():
  try:
    now = time.strftime('%H:%M:%S  %b %d')
    print("Display ip",now)
    ip_addr = subprocess.run('hostname -I'.split(),capture_output=True)
    ip_addr = ip_addr.stdout.split()[0].decode()
    print("ip: ",ip_addr)
    utils.lcd_string(ip_addr,LCD_LINE_2)
  except Exception as e:
    utils.lcd_string("No Internet",LCD_LINE_2)
    now = time.strftime('%H:%M:%S  %b %d')
    print("Got exception in ip",now)
    print(e)
  # time.sleep(4)

async def update_time():
  while True:
    # now,tm_min,tm_sec = utils.get_datetime()
    now = time.strftime('%H:%M:%S  %b %d')
    a= time.perf_counter()
    utils.lcd_string(now,LCD_LINE_1)
    b= time.perf_counter()
    # print(round(b-a,4))
    a = max(0,1-round(b-a,4))
    await asyncio.sleep(a)

async def update_weather(api_key):
  LOCATION = None
  now = time.strftime('%H:%M:%S  %b %d')
  print("Started updating weather",now)
  # has_fetched = True
  try:
    while True:
      now = time.strftime('%H:%M:%S  %b %d')
      if LOCATION is None:
        print(now,"\t","No Internet")
        utils.lcd_string("No Internet",LCD_LINE_2)
        await asyncio.sleep(4)
        # sleep(4)
        LOCATION = await utils.get_location()
        if LOCATION is not None:
          print(now,"\t","Restored Internet")
          display_ip()
          await asyncio.sleep(5)
          # sleep(5)


      else:
        # now = time.strftime('%H:%M:%S  %b %d')
        weather_data = await utils.get_weather_openweathermap(api_key,**LOCATION)
        print(now,"\t",weather_data)
        if weather_data == "No Weather data":
          LOCATION = await utils.get_location()
          if LOCATION is None:
            continue
        utils.lcd_string(weather_data,LCD_LINE_2)
        await asyncio.sleep(300)
        # sleep(300)
  except Exception as e:
    now = time.strftime('%H:%M:%S  %b %d')
    print(now)
    print(e)


async def main(api_keys):
  utils.lcd_init()
  # LOCATION = utils.get_location()
  # display_ip()
  # await asyncio.sleep(4)

  await asyncio.gather(
        update_time(),
        update_weather(api_keys["openweathermap"])
    )

  # asyncio.ensure_future(update_time())
  # asyncio.ensure_future(update_weather(api_keys["openweathermap"]))


if __name__ == '__main__':
  dirname = os.path.dirname(__file__) # absolute path of the script
  txt_path = os.path.join(dirname,"assets/api_keys.txt")
  pid = os.getpid()
  print("Current pid:",pid)
  # print("Current dir",dirname)
  # exit()
  try:
    with open(txt_path,"r") as f:
      api_keys = f.read().splitlines()
    api_keys= {k.split()[0]:k.split()[1] for k in api_keys}
    asyncio.run(main(api_keys))
  except KeyboardInterrupt:
    utils.lcd_init()
    utils.lcd_string("   Goodbye!!!   ",LCD_LINE_1)
    utils.lcd_string("  See you soon  ",LCD_LINE_2)
    time.sleep(3)
  finally:
    utils.lcd_byte(0x01, LCD_CMD)
