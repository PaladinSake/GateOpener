from openalpr import Alpr
from argparse import ArgumentParser
from PIL import Image
from pathlib import Path

print("imports done.")

parser = ArgumentParser(description='OpenALPR Python Test Program')

parser.add_argument("-c", "--country", dest="country", action="store", default="us",
                  help="License plate Country" )

parser.add_argument("--config", dest="config", action="store", default="/etc/openalpr/openalpr.conf",
                  help="Path to openalpr.conf config file" )

parser.add_argument("--runtime_data", dest="runtime_data", action="store", default="/usr/share/openalpr/runtime_data",
                  help="Path to OpenALPR runtime_data directory" )

parser.add_argument('plate_image', help='License plate image file')

print("arguments set.")

options = parser.parse_args()

def convert_to_greyscale(file_path):
    img = Image.open(file_path).convert('LA')
    output_file = 'greyscale_' + Path(file_path).stem + '.png'
    img.save(output_file)
    print('file saved as: ' + output_file)
            
def resize_image(file_path):
    basewidth = 300
    img = Image.open(file_path)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    
    output_file = 'resized_' + Path(file_path).stem + '.png'
    img.save(output_file)
    print('file saved as: ' + output_file)
    

def process_image(file_path):

    alpr.set_top_n(1)
    #alpr.set_default_region("au")
    alpr.set_detect_region(True)
    jpeg_bytes = open(file_path, "rb").read()
    results = alpr.recognize_array(jpeg_bytes)

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

            print 'Plate: ' + candidate['plate'], candidate['confidence']

    

alpr = None
try:
    print("begin try")
    alpr = Alpr(options.country, options.config, options.runtime_data)
    
    plate_image = options.plate_image
    
    print("Using OpenALPR " + alpr.get_version())

    if not alpr.is_loaded():
        print("Error loading OpenALPR")
    else:
        print("ALPR Loaded.")
        
        filename = (Path(plate_image).stem)
        
        print("Processing. Full Size Coloured..")
        process_image(plate_image)
        
        print("Resizing...")
        resize_image(plate_image)
        
        print("Processing Resized Coloured...")
        process_image('resized_' + filename + '.png')
        
        print('converting to greyscale...')
        convert_to_greyscale(plate_image)
        
        print("Processing Full Size Greyscale...")
        process_image('greyscale_' + filename + '.png')
        
        print("Resizing Greyscale...")
        resize_image('greyscale_' + filename + '.png')
        
        print("Processing Resized Greyscale...")
        process_image('resized_greyscale_' + filename + '.png')
        

finally:
    if alpr:
        alpr.unload()

    print("End finally.")