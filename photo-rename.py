#!/usr/bin/env python

from __future__ import print_function

from optparse import OptionParser
from PIL import Image
from PIL.ExifTags import TAGS

import errno, os, shutil, sys

options = \
    OptionParser(
        version = "%prog v1",
        usage = '%prog /path/to/the/photo',
        description = 'Simple Photo Renaming Tool',
        epilog = 'Example: ' + os.path.basename(sys.argv[0])
               + ' -d ../myphotos DSCN6529.JPG')

options.add_option('-d', '--destdir', default="./", dest="destdir", type="string",
        action='store', help='destination directory')
options.add_option('-v', '--verbose', default=False, dest="verbose",
        action='store_true', help='switch to the verbose mode')

def GetExifTags(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr(img, '_getexif'):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except:
        sys.stderr.write(
            '%s cannot be found, or the image cannot be opened and identified\n'
            % fname)
        sys.exit(1)

    return ret

def ForgeNewName(imageFile, destdir):
    fileName, fileExtension = os.path.splitext(imageFile)

    exifInfo = GetExifTags(imageFile)

    date, time = exifInfo['DateTime'].replace(':', '-').split()
    return "%s/%s_%s%s" % (destdir, date,time, fileExtension.lower())

def main():
    (opts, args) = options.parse_args()
    if len(args) < 1:
        options.print_help()
        return

    imageFileSrc = args[0]
    imageFileDst = ForgeNewName(imageFileSrc, opts.destdir)

    if opts.verbose:
        print(imageFileSrc + ' --> ' + imageFileDst)

    try:
        shutil.move(imageFileSrc, imageFileDst)
    except Exception as e:
        sys.stderr.write('An IO error occurred: %s\n' % e)
        sys.exit(1)

if __name__ == '__main__':
    main()

