import re
import requests
import argparse
import os
import sys
import textwrap

from resolutions import *

__author__ = 'BlexTw11'
__version__ = '1.2'
url_ifl = "https://interfacelift.com/"
url_sort = 'wallpaper/downloads/%s/any'
url_download_file = "wallpaper/7yz4ma1/"

def id_parser(r):
    return re.findall(r'id="list_([\d]+)"', r.content)

def name_parser(r, id):
    return re.search(r'javascript\:imgload\(\'(?P<name>.+)\'\, this\,\'%s\'\)' % id, r.content).group('name')

def next_page(r):
    link = re.search(r'href=\"(?P<link>.+\.html)\".+\>next page ', r.content).group('link')
    return requests.get(url_ifl + link)

def last_page(r):
    link = re.search(r'selector_disabled\".+\>next page ', r.content)
    return True if link else False

def find_resolution(r, id, resolution):
    regex = r'%s[\'\"\)\>\<\w\d\s\=:\/]*?Select Resolution[\'\"\)\>\<\w\d\s\=:\/_,\(.\-;]*?%s' % (id, resolution)
    res = re.search(regex, r.content)
    return True if res else False

def load_files(r, id, name, resolution, path):

    file_name = "%05d_%s_%s.jpg" % (int(id), name, resolution)
    url = url_ifl + url_download_file + file_name

    r_file = requests.get(url)
    # Schreibe die Daten in Dateien
    with open(path + "/" + file_name, "wb") as pic:
        pic.write(r_file.content)

    if r_file.status_code != requests.codes.ok:
        raise ValueError('Download picture failed')

def print_resolutions():
    string = 'Available resolutions are:\n'
    alt = 0
    for key,val in sorted(ifl_resolutions.items()):
        string += '\t{0:{fill}{align}35}'.format(key, fill=' ' if alt else '.', align='<') + "%s\n" % val
        alt ^= 1

    return string

def check_resolution(res, parser):
    if not res in ifl_resolutions.values():
        parser.print_help()
        print "\nError: Wrong resolution"
        sys.exit()

def arg_parser():
    resolutions = print_resolutions()
    parser = argparse.ArgumentParser(description='pyInterfaceLift v' + __version__ + ' by ' + __author__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(resolutions))
    parser.add_argument('resolution', help='Defines the resolution. E.g. 1920x1080')

    parser.add_argument('path', nargs='?', default=os.getcwd(),
                        help='Defines the path where the wallpapers will be stored.')
    parser.add_argument('-s', default='date', choices=['date', 'downloads', 'comments', 'rating', 'random'],
                        help='Sort the wallpapers on the Interfacelift page. Standard is "date".', dest='sort_by')
    parser.add_argument('-n', default=0, type=int, help='Defines the maximal downloaded wallpapers. '
                                                        'Standard is download all.', dest='max_download')

    return parser

def loop():
    try:
        parser = arg_parser()

        args = parser.parse_args()

        check_resolution(args.resolution, parser)

        r = requests.get(url_ifl + url_sort % args.sort_by)

        page_counter = 1
        wp_counter = 0

        while not last_page(r):
            ids = id_parser(r)
            print "*** Page [%d] ***\n" % page_counter
            page_counter += 1
            for id in ids:
                if find_resolution(r, id, args.resolution):
                    wp_counter += 1
                    print "Wallpaper [%d]" % wp_counter
                    print "Image ID:", id
                    name = name_parser(r, id)
                    print "Image Name:", name
                    load_files(r, id, name, args.resolution, args.path)
                if args.max_download > 0 and wp_counter == args.max_download:
                    print "All wallpapers downloaded. Bye!"
                    sys.exit()
            r = next_page(r)
        sys.exit()
    except KeyboardInterrupt:
        print "Exit..."

        sys.exit()

if __name__ == '__main__':
    loop()

