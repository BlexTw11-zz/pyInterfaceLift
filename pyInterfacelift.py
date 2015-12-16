import re
import requests
import argparse
import os
import sys

__author__ = 'BlexTw11'
__version__ = '1.1'
url_ifl = "https://interfacelift.com/"
url_sort = 'wallpaper/downloads/%s/any'
url_download_file = "wallpaper/7yz4ma1/"
set_sorted = ["date", "downloads", "comments", "rating", "random"]

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

def main():
    parser = argparse.ArgumentParser(description='pyInterfaceLift v' + __version__ + ' by ' + __author__)
    parser.add_argument('resolution', help='Defines the resolution. E.g. 1920x1080')
    parser.add_argument('path', nargs='?', default=os.getcwd(), help='Defines the path where the wallpapers will be stored.')
    parser.add_argument('-s', default='date', help='SORT_BY must be "date", "downloads", "comments", "rating" or "random". Sort the wallpapers on the Interfacelift page. Standard is "date".', dest='sort_by')
    parser.add_argument('-n', default=0, type=int, help='Defines the maximal downloaded wallpapers. Standard is all.', dest='max_download')
    args = parser.parse_args()

    resolution = args.resolution
    path = args.path
    max_wp = args.max_download
    if args.sort_by in set_sorted:
        sorted_by = args.sort_by
    else:
        print '\033[91m\n\tError: Wrong sorting command.\033[0m\n\tTry one of these: "date", "downloads", "comments", "rating" or "random".\n'
        parser.print_help()
        sys.exit()

    url = url_ifl + url_sort % sorted_by

    #print url

    r = requests.get(url)

    page_counter = 1
    wp_counter = 0

    while not last_page(r):
        ids = id_parser(r)
        print "*** Page [%d] ***\n" % page_counter
        page_counter += 1
        for id in ids:
            if find_resolution(r, id, resolution):
                wp_counter += 1
                print "Wallpaper [%d]" % wp_counter
                print "Image ID:", id
                name = name_parser(r, id)
                print "Image Name:", name
                load_files(r, id, name, resolution, path)
                print
            if max_wp > 0 and wp_counter == max_wp:
                print "All wallpapers downloaded. Bye!"
                sys.exit()
        r = next_page(r)
    sys.exit()


if __name__ == '__main__':
    main()