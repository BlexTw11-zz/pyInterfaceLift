import re
import requests
import argparse
import os
import sys
import textwrap

__author__ = 'BlexTw11'
__version__ = '1.3'
url_ifl = "https://interfacelift.com/"
url_sort = 'wallpaper/downloads/%s/any'
url_download_file = 'wallpaper/7yz4ma1/'
url_resolution = 'services/bulk_download_service/'
id_file = 'id'

ifl_resolutions = []


def id_parser(r):
    return re.findall(r'id="list_([\d]+)"', r.content)


def name_parser(r, wp_id):
    return re.search(r'javascript:imgload\(\'(?P<name>.+)\', this,\'%s\'\)' % wp_id, r.content).group('name')


def next_page(r):
    link = re.search(r'href=\"(?P<link>.+\.html)\".+>next page ', r.content).group('link')
    return requests.get(url_ifl + link)


def last_page(r):
    link = re.search(r'selector_disabled".+>next page ', r.content)
    return True if link else False


def find_resolution(r, wp_id, resolution):
    regex = r'%s[\'\"\)\>\<\w\d\s\=:\/]*?Select Resolution[\'\"\)\>\<\w\d\s\=:\/_,\(.\-;]*?%s' % (wp_id, resolution)
    res = re.search(regex, r.content)
    return True if res else False


def load_files(wp_id, name, resolution, path):
    file_name = "%05d_%s_%s.jpg" % (int(wp_id), name, resolution)

    url = url_ifl + url_download_file + file_name

    r_file = requests.get(url)
    with open(path + "/" + file_name, "wb") as pic:
        pic.write(r_file.content)

    if r_file.status_code != requests.codes.ok:
        raise Exception('Download picture failed')


def print_resolutions():
    string = 'Available resolutions are:\n'
    alt = 0
    for key, val in sorted(ifl_resolutions):
        string += '\t{0:{fill}{align}35}'.format(val, fill=' ' if alt else '.', align='<') + "%s\n" % key
        alt ^= 1

    return string


def check_resolution(res, parser):
    if res not in [item[0] for item in ifl_resolutions]:
        parser.print_help()
        print "\nError: Wrong resolution"
        sys.exit(-1)


def parse_resolution(r):
    global ifl_resolutions
    ifl_resolutions = list(set(re.findall(r'"(\d+x\d+)">(.*?)<', r.content)))


def read_latest_wp_id():
    try:
        if os.path.exists(id_file):
            f = open(id_file, 'r')
            wp_id = f.readline()
            f.close()
            return wp_id
    except IOError:
        print 'Error: Read file'
        sys.exit(-1)


def write_latest_wp_id(wp_id):
    try:
        f = open(id_file, 'w')
        f.write(wp_id)
        f.close()
    except IOError:
        print 'Error: Write file'
        sys.exit(-1)


def arg_parser():
    resolutions = print_resolutions()
    parser = argparse.ArgumentParser(description='pyInterfaceLift v' + __version__ + ' by ' + __author__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=textwrap.dedent(resolutions))
    parser.add_argument('resolution', help='Defines the resolution. E.g. 1920x1080')
    parser.add_argument('path', nargs='?', default=os.getcwd(),
                        help='Defines the path where the wallpapers will be stored.')
    parser.add_argument('-s', '--sort', default='date', choices=['date', 'downloads', 'comments', 'rating', 'random'],
                        help='Sort the wallpapers on the Interfacelift page. Standard is "date".', dest='sort_by')
    parser.add_argument('-n', '--max', default=0, type=int, help='Defines the maximal downloaded wallpapers. '
                        'Standard is download all.', dest='max_download')
    parser.add_argument('-c', '--cron', action='store_true', dest='cron',
                        help='Cron job mode. Saves the ID of the latest loaded '
                             'wallpaper and continues on the next job with just new wallpapers.')
    return parser


def loop():
    try:
        # Parse resolutions
        r = requests.get(url_ifl + url_resolution)
        parse_resolution(r)
        # Parse arguments
        parser = arg_parser()
        args = parser.parse_args()
        # Check if resolution is available on IFL
        check_resolution(args.resolution, parser)
        # Call IFL website
        r = requests.get(url_ifl + url_sort % args.sort_by)

        latest_wp_id = read_latest_wp_id()

        if not latest_wp_id and args.max_download == 0:
            parser.print_usage()
            print 'You try to use the cron job mode for the first time. Please call pyInterfaceLift with ' \
                  'switch "-n MAX>0" to initialize this mode.'
            sys.exit(1)

        page_counter = 1
        wp_counter = 0
        new_wp_id = None

        while not last_page(r):
            ids = id_parser(r)
            print "*** Page [%d] ***\n" % page_counter
            page_counter += 1
            if args.cron and not new_wp_id:
                new_wp_id = ids[0]
            for wp_id in ids:
                if args.cron and (not latest_wp_id or wp_id == latest_wp_id) \
                        and (0 < args.max_download == wp_counter or args.max_download == 0):
                    print "All new wallpapers downloaded. See u next time!"
                    write_latest_wp_id(new_wp_id)
                    sys.exit()
                if find_resolution(r, wp_id, args.resolution):
                    wp_counter += 1
                    print "Wallpaper [%d]" % wp_counter
                    print "Image ID:", wp_id
                    name = name_parser(r, wp_id)
                    print "Image Name:", name
                    print
                    load_files(wp_id, name, args.resolution, args.path)
                if 0 < args.max_download == wp_counter:
                    print "All wallpapers downloaded. Bye!"
                    sys.exit()
            r = next_page(r)
        sys.exit()
    except KeyboardInterrupt:
        print "Exit..."
        sys.exit()
    except ValueError as e:
        print e.message
        sys.exit(-1)


if __name__ == '__main__':
    loop()
