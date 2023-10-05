#!/usr/bin/env python
# A simple tool for renaming the photos created by a Nikon digital camera
# into something more meaningful.
# Copyright (C) 2015,2017,2023 Davide Madrisan <davide.madrisan@gmail.com>

from __future__ import print_function
from PIL import Image
from PIL.ExifTags import TAGS

import argparse
import errno
import glob
import os
import shutil
import sys


def parse_args():
    """This function parses and return arguments passed in"""
    progname = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        description="Simple photo renaming tool.",
        epilog=("examples:\n" + progname + " -d ~/Photos *.JPG myimage.jpg"),
    )
    parser.add_argument(
        "-d",
        "--destdir",
        action="store",
        help="specify a destination directory",
        dest="destdir",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite any existing output file",
        dest="force",
    )
    parser.add_argument(
        "-H",
        "--hidden",
        action="store_true",
        help="include hidden files and directories",
        dest="hidden",
    )
    parser.add_argument(
        "-m",
        "--move",
        action="store_true",
        help="move files instead of copying them",
        dest="move",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="check files and directories recursively",
        dest="recursive",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="execute this script in verbose mode",
        dest="verbose",
    )
    parser.add_argument("--version", action="version", version="%(prog)s version 1")
    parser.add_argument("images", nargs="+", help="the image file(s) to be renamed")

    return parser.parse_args()


def get_exif_tags(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr(img, "_getexif"):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except:
        sys.stderr.write(
            "%s cannot be found, or the image cannot be opened and identified\n" % fname
        )
        sys.exit(1)

    return ret


def forge_new_name(image, destdir):
    """
    Return the new filename and path, forged by using the exif data
    contained in the image file ('DateTime').
    Example: ~/Photos/2013-07-14_15-17-22.jpg
    """
    fileName, fileExtension = os.path.splitext(image)
    exifInfo = get_exif_tags(image)
    date, time = exifInfo["DateTime"].replace(":", "-").split()
    return "%s/%s_%s%s" % (destdir, date, time, fileExtension.lower())


def main():
    args = parse_args()
    destdir = args.destdir if args.destdir else "."
    images = set(
        [
            img
            for arg in args.images
            for img in glob.glob(
                arg, include_hidden=args.hidden, recursive=args.recursive
            )
        ]
    )

    if not os.path.exists(destdir):
        try:
            os.makedirs(destdir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    for image in images:
        destfile = forge_new_name(image, destdir)
        if args.verbose:
            print(image + " --> " + destfile)

        if os.path.isfile(destfile) and not args.force:
            sys.stderr.write(
                "The destination file exists, skipping {0}\n".format(destfile)
            )
            continue

        try:
            if args.move:
                shutil.move(image, destfile)
            else:
                shutil.copy2(image, destfile)
        except Exception as e:
            sys.stderr.write("An IO error occurred: %s\n" % e)
            continue


if __name__ == "__main__":
    main()
