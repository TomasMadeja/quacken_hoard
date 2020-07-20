import sys
import time
import re
import argparse
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent

import yaml

import requests


class Processor():
    def __init__(self, url):
        self.__url = url
    
    def report(self, filePath):
        filePath = Path(filePath).absolute()
        with filePath.open('rb') as f:
            r = requests.post(
                self.__url, 
                files={
                    filePath.name : f
                }
            ) 


class DirEventHandler(FileSystemEventHandler):

    def __init__(self, regex, processor):
        super().__init__()
        self.__regex: re.Pattern = regex
        self.__processor = processor

    def on_moved(self, event):
        self.process(event)

    def process(self, event):
        if (
            isinstance(event, FileMovedEvent) and 
            self.path_matches(event.dst_path)
        ):
            self.__processor.report(event.dst_path)

    def path_matches(self, raw_path):
        name = Path(raw_path).absolute().name
        return self.__regex.fullmatch(name) is not None


class DirWatcher:
    def __init__(self):
        self.__registered_events = []
        self.__event_observer = Observer()
    

    def add(self, path, handler):
        self.__registered_events.append((path, handler))

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        for (path, handler) in self.__registered_events:
            self.__event_observer.schedule(
                handler,
                str(path),
                recursive=True
            )

EXAMPLE = """
watchers:
    - dir: "path"
      regex: "a:pcap"
      reporter: "a:default"

    - dir: "path"
      regex: "^archived_.*\\.(?:pcapng|pcap|cap)$"
      reporter: 
        url: "http://smthing"

aliases:
    reporters:
      - alias: "default"
        url: "http://smthing"
    regexes:
       - alias: "pcap"
         regex: "^archived_.*\\.(?:pcapng|pcap|cap)$"
"""

def parse_yaml(config: Path) -> dict:
    with config.open("r") as fhandle:
        parsed_data = yaml.load(fhandle, Loader=yaml.SafeLoader)
    return parsed_data

def parse_config(config_path: Path):
    watcher = DirWatcher()
    config = parse_yaml(config_path)

    regex_aliases = {}
    for record in config["aliases"]["regexes"]:
        regex_aliases[record["alias"]] = re.compile(record["regex"])

    reporter_aliases = {}
    for record in config["aliases"]["watchers"]:
        reporter_aliases[record["alias"]] = Processor(record["url"])
    
    for watcher in config["watchers"]:
        regex_raw:str = watcher["regex"]
        if regex_raw.startswith("a:"):
            regex = regex_aliases[regex_raw[2:]]
        else:
            regex = re.compile(regex_raw)
        reporter_raw = watchers["reporter"]
        if isinstance(reporter_raw, str):
            reporter = reporter_aliases[reporter_raw]
        else:
            reporter = Processor(reporter_raw["url"])
        
        watcher.add(
            Path(watcher['dir']).absolute(),
            DirEventHandler(regex, reporter)
        )


if __name__ == "__main__":
    description = (
        "Script for resending files, that watches for move "
        "and rename in a directory, and send+deletes the matching file."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config', help='Path to a yaml config file.', type=Path, required=True)

    args = parser.parse_args()

    dir_watcher = parse_config(args.config)
    dir_watcher.run()
