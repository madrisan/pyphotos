#!/usr/bin/env python

from __future__ import print_function
from PIL import Image
from PIL.ExifTags import TAGS

import argparse, errno, os, shutil, sys

parser = argparse.ArgumentParser(
    description = 'Simple photo renaming tool.',
    epilog = 'example: ' + os.path.basename(sys.argv[0])
           + ' -d ../myphotos DSCN6529.JPG')
parser.add_argument(
    "-d", "--destdir",
    action = "store",
    help   = "specify a destination directory",
    dest   = "destdir")
parser.add_argument(
    "-f", "--force",
    action = "store_true",
    help   = "overwrite any existing output file",
    dest   = "force")
parser.add_argument(
    "-v", "--verbose",
    action = "store_true",
    help   = "execute this script in verbose mode",
    dest   = "verbose")
parser.add_argument(
    "--version", action = "version", version = "%(prog)s version 1")
parser.add_argument(
    "imageFile", help = "the image file to be renamed")

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
    args = parser.parse_args()
    destdir = args.destdir if args.destdir else '.'

    imageFileDst = ForgeNewName(args.imageFile, destdir)

    if args.verbose:
        print(args.imageFile + ' --> ' + imageFileDst)

    if (os.path.isfile(imageFileDst) and not args.force):
        sys.stderr.write(
            'The destination file %s already exists\n' % imageFileDst)
        sys.exit(1)

    try:
        shutil.move(args.imageFile, imageFileDst)
    except Exception as e:
        sys.stderr.write('An IO error occurred: %s\n' % e)
        sys.exit(1)

if __name__ == '__main__':
    main()
