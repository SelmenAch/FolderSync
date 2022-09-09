# FolderSync
A folder synchronization program that synchronizes files from a source directory to a replica directory by checking file checksums.

## Usage
---
#### Step 1) Setup the settings.ini file

1. **Manually setup settings.ini:**<br>
Open the settings.ini file provided in the repository and modify the settings as needed.
2. **Run the setup utility for settings.ini:**<br>
Run the python program with the following launch parameter:  
`--setup`

#### Step 2) After setting up the settings.ini file, run the program using:
`python FolderSync/`

## Optional parameters
```
--h/--help: Displays all available commands.
--setup: Initializes setup mode with an interactive settings.ini creation utility.
--debug: Enables console print messages.
--sync-interval <int>: Sets the time interval in seconds between directory synchronization.
--hash <algorithm>: Sets the hashing algorithm to use for checksums.
        Supported hashing algorithms: [md5, sha1, sha224, sha256, sha384, sha512, crc32, adler32]
```

## Requirements
- Python 3.7+
