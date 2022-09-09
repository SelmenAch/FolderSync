from pathlib import Path
from os import getcwd

def source_dir_setup():
    source_dir_prompt = input('Please enter your source directory path:\n')
    while len(source_dir_prompt) == 0:
        source_dir_prompt = input('Please enter your source directory path:\n')
    return source_dir_prompt


def replica_dir_setup():
    replica_dir_prompt = input('Please enter your replica directory path:\n')
    while len(replica_dir_prompt) == 0:
        replica_dir_prompt = input('Please enter your replica directory path:\n')
    return replica_dir_prompt

def log_file_setup():
    log_file_prompt = input('Please enter your log file path:\n')
    while len(log_file_prompt) == 0:
        log_file_prompt = input('Please enter your log file path:\n')
    return log_file_prompt
	
def setup_settings():
    print("Welcome to the FolderSync settings setup utility.\nThis utility will help you set up the settings.ini file.\n")
    source_dir = source_dir_setup()
    replica_dir = replica_dir_setup()
    log_file = log_file_setup()

    with open(Path(getcwd(), 'settings.ini'), 'w') as settings:
        settings.write(
            "[Main_Settings]\n"
            "; Source directory\n"
            f"SourceDirectory = {source_dir}\n"
            "; Replica directory\n"
            f"ReplicaDirectory = {replica_dir}\n"
            "; Log file\n"
            f"LogFile = {log_file}\n"
        )
        print("settings.ini file creation complete!")

