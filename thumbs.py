import glob
import os
from PIL import Image, ImageOps, ImageFile
import sys

ImageFile.LOAD_TRUNCATED_IMAGES = True

def create_thumbs(directory):
    '''
        Creates thumbs for the specified directory.
        Saves the thumbs in folder static/thumbs/
    '''
    size = 180,180
    thumb_directory = 'static/thumbs/'
    image_extensions = ('jpg','jpeg',
                        'png','gif',
                        'tiff')

    # Gets all files in directory
    count = 0
    for infile in glob.glob(directory + "/*.*"):
        f, ext = os.path.splitext(infile)

        # Checks if a file is image
        if ext[1:].lower() in image_extensions:

            # Gets the path of image
            # Creates a path for the thumbnail image
            path = os.path.dirname(infile)
            path = path.replace("static/", "", 1)
            path = thumb_directory + path

            # If path of thumbnail is not existing
            # Create the directory and its sub-directories
            if not os.path.exists(path):
                os.makedirs(path)

            # get the bare filename of image without extensions
            filename = os.path.basename(f)
            print 'Get Filename: %s' % filename
            # Pillow does not like jpg so convert it to jpeg
            if ext.lower() == ".jpg":
                ext = ".jpeg"

            # Open the image if it does not yet have a thumbnail
            if not glob.glob(path + "/" + filename + ext):
                im = Image.open(infile)

                # Creates a new thumbnail for none GIF
                # Gif images are not converted just
                # resave
                #if ext.lower() not in ('gif'):
                #    im.thumbnail(size, Image.ANTIALIAS)
                im = ImageOps.fit(im, size, method=Image.ANTIALIAS)

                # Save the image with its appropriate
                # name and extension
                im.save(path + "/" + filename + ext, ext[1:])
                print 'done saving %s' % filename

def start():
    directory = 'static/uploads/Pictures'
    dirs = os.walk(directory).next()[1]
    for d in dirs:
        print "now switching dir to %s" % d
        path = directory + '/' + d
        create_thumbs(path)

def opt(arg1):
    option = arg1
    start()

if __name__=='__opt__':
    sys.exit(opt(sys.argb[1]))
