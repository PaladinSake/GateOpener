from openalpr import Alpr
from argparse import ArgumentParser
from PIL import Image
from pathlib import Path
from time import sleep
#import RPi.GPIO as GPIO
import os
import shutil
import time
import re
import json
from picamera import PiCamera

print("imports done.")

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(11, GPIO.IN)
#GPIO.setup(3, GPIO.OUT)

print('GPIO setup complete.')

def convert_to_greyscale(file_path):
    splitpath = os.path.split(file_path)
    directory = splitpath[0]
    
    img = Image.open(file_path).convert('LA')
    output_file = directory + '/greyscale_' + Path(file_path).stem + '.png'
    img.save(output_file)
    print('file saved as: ' + output_file)
            
def resize_image(file_path):
    splitpath = os.path.split(file_path)
    directory = splitpath[0]
    
    basewidth = 300
    img = Image.open(file_path)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    
    output_file = directory + '/resized_' + Path(file_path).stem + '.png'
    img.save(output_file)
    print('file saved as: ' + output_file)
    

def process_image(file_path):

    alpr.set_top_n(1)
    #alpr.set_default_region("au")
    alpr.set_detect_region(True)
    jpeg_bytes = open(file_path, "rb").read()
    results = alpr.recognize_array(jpeg_bytes)

    plate_text = 'No Plate Found.'
    plate_confidence = 0

    # Uncomment to see the full results structure
    # import pprint
    # pprint.pprint(results)

    print("Image size: %dx%d" %(results['img_width'], results['img_height']))
    print("Processing Time: %f" % results['processing_time_ms'])

    i = 0
    for plate in results['results']:
        i += 1
        for candidate in plate['candidates']:
            prefix = "-"
            if candidate['matches_template']:
                prefix = "*"
                plate_text = candidate['plate']
                plate_confidence = candidate['confidence']

            print 'Plate: ' + plate_found + ' ' + str(plate_confidence) + '%'
            
    return plate_text

def capture_image():
    camera=PiCamera()
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/GateOpener/Images/CapturedImage.jpg')
    camera.stop_preview()
    
def archive_images():
    time_string = time.strftime("%Y%m%d-%H%M%S")
    
    for dir_item in os.listdir(basepath):
        
        fullpath = os.path.join(basepath, dir_item)
        
        if os.path.isdir(fullpath):
            #Skip directory items.
            print('skip directory item.')
        elif not os.path.isdir(fullpath):
            print('Moving ' + fullpath + ' to Archive...')
            shutil.move(basepath + "/"+dir_item, basepath + "/Archive/" + time_string + "-" + dir_item)
            
def validate_access(vehicle_plate):
    print('validating access...')
    
    permission = False
    
    with open('ApprovedPlates.json') as access_list:
        data = access_list.read()
        
    print('data defined.')
        
    obj = json.loads(data)
    
    for approved_plate in obj["Numberplate List"]:
        
        if vehicle_plate == approved_plate['Plate']:
           permission = True
        
        
    return permission
    
alpr = None
try:
    
    country = 'us'
    config = '/etc/openalpr/openalpr.conf'
    runtime_data = '/usr/share/openalpr/runtime_data'
    basepath = 'Images'
    
    i=0
    
    print("begin try")
    alpr = Alpr(country, config, runtime_data)
    
    plate_image = basepath + "/CapturedImage.jpg"
    
    print("Using OpenALPR " + alpr.get_version())

    if not alpr.is_loaded():
        print("Error loading OpenALPR")
    else:
        print("ALPR Loaded.")
        
        #while True:
        while i<=10:
            
            #input = GPIO.input(11)
            #if input == 0:
            if i<10:
                print "No Movement."
                #GPIO.output(3, 0) # Turn light off.
            #elif input == 1:
            elif i==10:
                print('Movement Detected')
                #GPIO.output(3,1) # Turn light on.
                
                capture_image()
            
                filename = (Path(plate_image).stem)
                
                print('converting to greyscale...')
                convert_to_greyscale(plate_image)
                
                print("Resizing Greyscale...")
                resize_image(basepath + '/greyscale_' + filename + '.png')
                
                print("Processing Resized Greyscale...")
                numberplate_output = process_image(basepath + '/resized_greyscale_' + filename + '.png')
                
                if re.search('[0-9]', numberplate_output):
                    print('digit found.')
                else:
                    print('nothing')
                    
                approval = validate_access(numberplate_output)
                
                if approval == True:
                    print 'Access Granted. Opening Gate...'
                else:
                    print 'Access Denied. Manual Gate open Required.'
                
                archive_images()
            
            sleep(0.1)
            
            i=i+1
        

finally:
    if alpr:
        alpr.unload()

    print("End finally.")