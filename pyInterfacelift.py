import re
import requests

__author__ = 'BlexTw11'
__version__ = '0.1'
url_start = "https://interfacelift.com/"
url_start_wp = "https://interfacelift.com/wallpaper/"
url = 'https://interfacelift.com/wallpaper/downloads/date/index1.html'
url_download_fix = "/7yz4ma1/"

def id_parser(r):
    #return re.search(r'id="list_(?P<id>[\d]+)"', r.content).group('id')
    return re.findall(r'id="list_([\d]+)"', r.content)

def name_parser(r, id):
    return re.search(r'javascript\:imgload\(\'(?P<name>.+)\'\, this\,\'%s\'\)' % id, r.content).group('name')
    #return re.findall(r'javascript\:imgload\(\'(.+)\'\, this\,\'%s\'\)' % id, r.content)

def next_page(r):
    link = re.search(r'href=\"(?P<link>.+\.html)\".+\>next page ', r.content).group('link')
    return requests.get(url_start + link)

def last_page(r):
    link = re.search(r'selector_disabled\".+\>next page ', r.content)
    return True if link else False

def find_resolution(r, id, resolution):
    res = re.search(
            r'\<div id=\"list_%s\"\>.*%s.*\<div style=\"clear: both; padding: 0; margin: 0; height: 0;\"\>\</div\>'
            % (id, resolution), r.content)
    print res
    return True if res else False

def load_files(r, id, name, resolution):

    file_name = "%05d_%s_%s.jpg" % (id, name, resolution)
    print file_name
    url = url_start_wp + url_download_fix + file_name
    print url

    r_file = requests.get(url)
    # Schreibe die Daten in Dateien
    with open(file_name, "wb") as pic:
        pic.write(r_file.content)

    if r_file.status_code != requests.codes.ok:
        raise ValueError('Download picture failed')

def main():
    #parser = argparse.ArgumentParser(description='pyInterfaceLift v' + __version__ + ' by ' + __author__)
    #parser.add_argument('-d', '--debug', action='store_true', help='Debug mode. Downloads not really a file.', dest='debug')
    #parser.add_argument('-s', '--single', action='store_true', help='Download just a single file.', dest='single')
    #args = parser.parse_args()

    r = requests.get(url)

    resolution = '3840x2160'

    while not last_page(r):
        ids = id_parser(r)
        for id in ids:
            print "Image ID:", id
            name = name_parser(r, id)
            print "Image Name:", name
            if find_resolution(r, id, resolution):
                load_files(r, id, name, resolution)



if __name__ == '__main__':
    main()