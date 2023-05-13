import os
import  urllib.parse
import types
import time 

import qbittorrentapi
from dotenv import load_dotenv
from tqdm import tqdm
import schedule

load_dotenv()

HOST_NAME=types.SimpleNamespace()
HOST_NAME.IPV4="tracker.m-team.cc"
HOST_NAME.IPV6="ipv6.tracker.m-team.cc"

def check_trackers(trackers:qbittorrentapi.TrackersList):
    ipv4,ipv6=None,None
    for tracker in trackers:
        url:urllib.parse.ParseResult=urllib.parse.urlparse(tracker.url)
        match url.netloc:
            case HOST_NAME.IPV4 :
                ipv4=url
            case HOST_NAME.IPV6 :
                ipv6=url
    return ipv4,ipv6

def url_replace_netloc(url:urllib.parse.ParseResult,netloc):
    url=urllib.parse.ParseResult(scheme=url.scheme, netloc=netloc, path=url.path, params=url.params, query=url.query, fragment=url.fragment)
    return url

def scan_add_tracker():

    conn_info = dict(
        host=os.getenv("QBITTORRENT_HOST_NAME") or "localhost",
        port=os.getenv("QBITTORRENT_PORT") or 8080,
        username=os.getenv("QBITTORRENT_USER_NAME") or "admin",
        password=os.getenv("QBITTORRENT_PASS_WORD") or "adminadmin",
    )
    # or use a context manager:
    with qbittorrentapi.Client(**conn_info) as qbt_client:
        qbt_client:qbittorrentapi.Client=qbt_client
        # display qBittorrent info
        print(f"qBittorrent: {qbt_client.app.version}, qBittorrent Web API: {qbt_client.app.web_api_version}")

        # retrieve and show all torrents
        for torrent in  tqdm(qbt_client.torrents_info()):
            ipv4,ipv6 =check_trackers(torrent.trackers)
            if ipv4 and (not ipv6):
                ipv6=url_replace_netloc(ipv4,HOST_NAME.IPV6)
                tqdm.write(f"{torrent.hash[-6:]}: {torrent.name} add ipv6")
                torrent.add_trackers(urls=[ipv6.geturl(),])

            elif ipv6 and (not ipv4):
                ipv4=url_replace_netloc(ipv6,HOST_NAME.IPV4)
                tqdm.write(f"{torrent.hash[-6:]}: {torrent.name} add ipv4")
                torrent.add_trackers(urls=[ipv4.geturl(),])

if __name__ == "__main__":
    scan_time=int(os.getenv("SCAN_SECONDS")) or 300
    schedule.every(scan_time).seconds.do(scan_add_tracker)
    while True:
        schedule.run_pending()
        time.sleep(scan_time//5 or 1 )