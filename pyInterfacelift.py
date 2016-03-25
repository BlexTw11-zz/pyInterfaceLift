import re
import requests
import argparse
import os
import sys
import textwrap

__author__ = 'BlexTw11'
__version__ = '1.4'

# Timeout for http request
timeout = 5  # seconds

url_ifl = 'https://interfacelift.com/'
url_sort = 'wallpaper/downloads/%s/any'
url_download_file = 'wallpaper/7yz4ma1/'
url_resolution = 'services/bulk_download_service/'
id_file = 'id'

ifl_resolutions = []
last_file_name = None

MB_IN_BYTES = 1048576


def get_request(url, stream=False):
    try:
        return requests.get(url, stream=stream, timeout=timeout)
    except requests.exceptions.Timeout as error:
        print 'Timeout. Perhaps the server is down?! :(\n\nError Message:'
        print '\t', error.message
        sys.exit(-1)
    except requests.exceptions.ConnectionError as error:
        print 'Connection Error. Something went terrible wrong... sorry.\n\nError Message:'
        print '\t', error.message
        sys.exit(-2)


def id_parser(r):
    return re.findall(r'id="list_([\d]+)"', r.content)


def file_name_parser(r, wp_id):
    return re.search(r'javascript:imgload\(\'(?P<name>.+)\', this,\'%s\'\)' % wp_id, r.content).group('name')


def wp_name_parser(r, wp_id):
    return re.search(r'<h1.*?%s.*html">(?P<name>.+)</a>' % wp_id, r.content).group('name')


def next_page(r):
    link = re.search(r'href=\"(?P<link>.+\.html)\".+>next page ', r.content).group('link')
    return requests.get(url_ifl + link)


def last_page(r):
    link = re.search(r'selector_disabled".+>next page ', r.content)
    return link is not None


def find_resolution(r, wp_id, resolution):
    re_resolution = re.compile(r'%s[\'\"\)><\w\d\s=:/]*?Select Resolution[\'\"\)><\w\d\s=:/_,\(.\-;]*?%s' % (wp_id, resolution))
    res = re_resolution.search(r.content)
    return res is not None


def load_files(r, wp_id, resolution, path):
    global last_file_name
    name = file_name_parser(r, wp_id)
    file_name = '%05d_%s_%s.jpg' % (int(wp_id), name, resolution)
    # Save temporary the current downloaded file
    last_file_name = path + '/' + file_name
    url = url_ifl + url_download_file + file_name

    with open(last_file_name, 'wb') as wp:
        response = get_request(url, stream=True)
        total_length = response.headers.get('content-length')

        if not total_length:
            wp.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            length_string = '%.2f %s' % (float(total_length)/(1024 if total_length < MB_IN_BYTES else MB_IN_BYTES),
                                         'kBytes' if total_length < MB_IN_BYTES else 'MBytes')

            for data in response.iter_content(chunk_size=2048):
                dl += len(data)
                wp.write(data)
                sys.stdout.write('\r%-50s %.2f %s of %s   ' % (u'\u2588' * (50 * dl / total_length),
                                                               float(dl)/(1024 if dl < MB_IN_BYTES else MB_IN_BYTES),
                                                               'kBytes' if dl < MB_IN_BYTES else 'MBytes', length_string))
                sys.stdout.flush()
    print
    last_file_name = None
    if response.status_code != requests.codes.ok:
        raise Exception('Download picture failed')


def print_resolutions():
    string = 'Available resolutions are:\n'
    alt = 0
    for key, val in sorted(ifl_resolutions):
        string += '\t{0:{fill}{align}35}'.format(val, fill=' ' if alt else '.', align='<') + '%s\n' % key
        alt ^= 1
    return string


def check_resolution(res, parser):
    if res not in [item[0] for item in ifl_resolutions]:
        parser.print_help()
        print '\nError: Wrong resolution'
        sys.exit(-1)


def parse_resolution(r):
    global ifl_resolutions
    ifl_resolutions = list(set(re.findall(r'"(\d+x\d+)">(.*?)<', r.content)))


def read_latest_wp_id():
    re_id = re.compile(r'(?P<sorting>\w+) (?P<id>\d+)')
    wp_id = {}

    try:
        if os.path.exists(id_file):
            f = open(id_file, 'r')

            for line in f:
                res = re_id.search(line)
                if res:
                    wp_id[res.group('sorting')] = res.group('id')
            f.close()
            return wp_id

    except IOError:
        print 'Error: Read file'
        sys.exit(-1)


def write_latest_wp_id(wp_id):
    try:
        f = open(id_file, 'w')

        for k in wp_id:
            f.write('%s %s\n' % (k, wp_id[k]))
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
                        'Standard is download all.', dest='max_wallpaper')
    parser.add_argument('-c', '--cron', action='store_true', dest='cron',
                        help='Cron job mode. Saves the ID of the latest loaded '
                             'wallpaper and continues on the next job with just new wallpapers.')
    return parser


def loop(r, args, latest_wp_id):
    page_counter = 1
    wp_counter = 0
    new_wp_id = None

    while True:
        ids = id_parser(r)
        print '*** Page [%d] ***\n' % page_counter
        page_counter += 1

        if args.cron and not new_wp_id:
            new_wp_id = latest_wp_id.copy()
            new_wp_id[args.sort_by] = ids[0]
            write_latest_wp_id(new_wp_id)

        for wp_id in ids:
            if args.cron and (args.sort_by in latest_wp_id and wp_id == latest_wp_id[args.sort_by]):
                print 'All new wallpapers downloaded. See u next time!'
                sys.exit()

            if find_resolution(r, wp_id, args.resolution):
                wp_counter += 1
                print 'Wallpaper [%d]' % wp_counter
                print 'Image ID:', wp_id
                name = wp_name_parser(r, wp_id)
                print 'Image Name:', name
                load_files(r, wp_id, args.resolution, args.path)
                print

            if 0 < args.max_wallpaper == wp_counter:
                print 'All wallpapers downloaded. Bye!'
                sys.exit()

        r = next_page(r)

        if last_page(r):
            print 'Reached last page. Bye!'
            sys.exit()


def main():
    try:
        # Parse resolutions
        r = get_request(url_ifl + url_resolution)
        parse_resolution(r)
        # Parse arguments
        parser = arg_parser()
        args = parser.parse_args()
        # Check if resolution is available on IFL
        check_resolution(args.resolution, parser)
        # Call IFL website
        r = get_request(url_ifl + url_sort % args.sort_by)

        latest_wp_id = read_latest_wp_id()

        if not latest_wp_id and args.max_wallpaper == 0:
            parser.print_usage()
            print 'You try to use the cron job mode for the first time. Please call pyInterfaceLift with ' \
                  'switch "-n MAX>0" to initialize this mode.'
            sys.exit(1)

        loop(r, args, latest_wp_id)

    except KeyboardInterrupt:
        if last_file_name:
            os.remove(last_file_name)
        print '\nExit...'
        sys.exit()

    except Exception as e:
        print e.message
        sys.exit(-1)


if __name__ == '__main__':
    main()
