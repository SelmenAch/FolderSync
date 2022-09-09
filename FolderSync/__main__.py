import argparse
import configparser
from setup_utility import setup_settings
from resources.strings import *
from main import FileSynchronizer
from os import getcwd, path
from pathlib import Path
from sys import exit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Synchronizes files from source directory to replica directory by checking individual file checksums."
    )
    parser.add_argument('--debug', dest='debug_mode', action='store_true', default=True, help='Enables console print messages')
    parser.add_argument('--sync-interval', dest='sync_interval', default=5, help='Sets the time interval in seconds between directory synchronization')
    parser.add_argument('--hash', dest='hash_algorithm', default='sha256',
                        help='Sets the hashing algorithm to use for checksums\n'
                             'Supported hashing algorithms: [md5, sha1, sha224, sha256, sha384, sha512, crc32, adler32]')
    parser.add_argument('--setup', dest='setup_mode', action='store_true', default=False, help='Initializes setup mode with an interactive settings.ini creation utility')

    args = parser.parse_args()
    if args.setup_mode:
        setup_settings()
        exit(0)

    config = configparser.ConfigParser()
    config.read('settings.ini')
    if config is None or not path.isfile(Path(getcwd(), 'settings.ini')):
        print("Error with the settings.ini file. Please make sure the file exists in the root directory of the program.")
        exit(-1)
    if not path.isdir(config[MAIN_SETTINGS][SOURCE_DIR]):
        print(f"Source directory error in settings.ini file. Please make sure the {SOURCE_DIR} is a valid directory.")
        exit(-1)
    if not path.isdir(config[MAIN_SETTINGS][REPLICA_DIR]):
        print(f"Replica directory error in settings.ini file. Please make sure the {REPLICA_DIR} is a valid directory.")
        exit(-1)	
    if not path.isfile(config[MAIN_SETTINGS][LOG_FILE]):
        print(f"Log file error in settings.ini file. Please make sure the {LOG_FILE} is a valid txt file.")
        exit(-1)
    
    synchronizer = FileSynchronizer(config=config, debug=args.debug_mode, hash_algo=args.hash_algorithm, sync_interval=int(args.sync_interval))
