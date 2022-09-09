import errno
import shutil
from resources.strings import *
from hashlib import md5, sha1, sha224, sha256, sha384, sha512 
from zlib import crc32, adler32
from time import sleep
from os import walk, remove
from pathlib import Path

# Resolves hash algorithm.
class HashResolver:
    def __init__(self, debug=False):
        self.debug = debug

    # Resolves hash algorithm provided by user and returns the hash object.
    @staticmethod
    def hash_identifier(given_hash: str):
        if given_hash.lower() == H_MD5:
            return md5()
        if given_hash.lower() == H_SHA_1:
            return sha1()
        if given_hash.lower() == H_SHA_224:
            return sha224()
        if given_hash.lower() == H_SHA_256:
            return sha256()
        if given_hash.lower() == H_SHA_384:
            return sha384()
        if given_hash.lower() == H_SHA_512:
            return sha512()
        else:
            return None

# Manages copying and deleting files.
class FileManager:
    def __init__(self, config, debug=True):
        self.config = config
        self.debug = debug
		
    # Deletes files that no longer exist in source directory.
    def delete_file(self, file_path):
            try:
                remove(file_path)
                if self.debug:
                    print(f"Deleted file in replica directory: [{file_path.as_posix()}]")
                    log_file_path = self.config[MAIN_SETTINGS][LOG_FILE]
                    log_file = open(log_file_path, 'a')
                    log_file.write(f"Deleted file in replica directory: [{file_path.as_posix()}]\n")
                    log_file.close()

                return True
            except OSError as e:
                # Reports file read/write permission errors.
                if e.errno == errno.EPERM:
                    if self.debug:
                        print(f"File permission error while deleting files:\n{e}")
                    return False
                else:
                    if self.debug:
                        print(f"Error while deleting files:\n{e}")
                    return False

    # Copies files from a source directory to a replica directory.
    def copy_file(self, source_file_path, replica_file_path):
            # Copies the files
            try:
                shutil.copy(source_file_path, replica_file_path)
                if self.debug:
                    print(f"Copied file in replica directory: [{source_file_path.as_posix()}]")
                    log_file_path = self.config[MAIN_SETTINGS][LOG_FILE]
                    log_file = open(log_file_path, 'a')
                    log_file.write(f"Copied file in replica directory: [{source_file_path.as_posix()}]\n")
                    log_file.close()	
            except OSError as e:                    
                # Reports file read/write permission errors.
                if e.errno == errno.EPERM:
                    if self.debug:
                        print(f"File permission error while copying files:\n{e}")
                else:
                    if self.debug:
                        print(f"Error while copying files:\n{e}")


# Scans the source directory for file modifications by checksum and synchronizes files to replica directory.
class FileSynchronizer:
    def __init__(self, config, hash_algo, sync_interval, debug=True):
        self.config = config
      
        self.hash = hash_algo
        # Reports an error if an unsupported hash algorithm is provided by the user.
        if self.hash != H_CRC_32 and self.hash != H_ADLER_32:
            if HashResolver.hash_identifier(self.hash) is None:
                print(f"Error while resolving the hash algorithm type: {self.hash}\nPlease provide a supported hash.")
                return
        self.sync_interval = sync_interval
        self.debug = debug
        self.hasher = None
        self.hash_resolver = HashResolver(debug=self.debug)
        self.copier = FileManager(debug=self.debug, config=self.config)
        self.hash_dict = {}

        self.source_scan()

    def source_scan(self):
        while True:
            self.scan_directory()
            sleep(self.sync_interval)

    def delete_missing_files(self, dir_path, file_names):
        keys_to_delete = []
        for item in self.hash_dict.keys():
            if item.split('/')[-1] not in file_names:
                if self.debug:
                    print(f"Missing file from hash dictionary: {item}\nRemoving {item} from replica directory...")
                parent_dir = dir_path.rsplit('/', 1)
                if len(parent_dir) == 0:
                    parent_dir = dir_path.rsplit('\\', 1)
                parent_dir = parent_dir[1]
                replica_path = self.config[MAIN_SETTINGS][REPLICA_DIR]
                replica_file_path = Path(replica_path, item.split('/')[-1])
                if self.copier.delete_file(replica_file_path):
                    keys_to_delete.append(item)
        for key in keys_to_delete:
            del self.hash_dict[key]

    def copy_file_to_replica(self, dir_path, file_names):
        file_modified = False
        for i, file in enumerate(file_names):
            if self.check_file(Path(dir_path, file)):
                file_modified = True
                parent_dir = dir_path.rsplit('/', 1)
                if len(parent_dir) == 0:
                    parent_dir = dir_path.rsplit('\\', 1)
                parent_dir = parent_dir[1]

                replica_path = self.config[MAIN_SETTINGS][REPLICA_DIR]
                replica_file_path = Path(replica_path,file)
                self.copier.copy_file(Path(dir_path, file), replica_file_path)
        return file_modified

    def check_file(self, file) -> bool:
        self.hasher = HashResolver.hash_identifier(self.hash)
        use_crc32 = False
        use_adler32 = False
        if self.hash == H_CRC_32:
            use_crc32 = True
        if self.hash == H_ADLER_32:
            use_adler32 = True
        with open(file, 'rb') as cur_file:
            buffer = cur_file.read()
            try:
                if self.hasher is not None:
                    if not use_crc32 and not use_adler32:
                        self.hasher.update(buffer)
                else:
                    if use_crc32:
                        self.hasher = crc32(buffer, 0)
                    elif use_adler32:
                        self.hasher = adler32(buffer, 0)
                    else:
                        return False
            except RuntimeError as e:
                print(f"Error while hashing:\n{e}")
                return False

            while len(buffer) > 0:
                buffer = cur_file.read()
                try:
                    if self.hasher is not None:
                        if not use_crc32 and not use_adler32:
                            self.hasher.update(buffer)
                    else:
                        if use_crc32:
                            self.hasher = crc32(buffer, self.hasher)
                        elif use_adler32:
                            self.hasher = adler32(buffer, self.hasher)
                        else:
                            return False
                except RuntimeError as e:
                    print(f"Error while hashing:\n{e}")
                    return False

        if not use_crc32 and not use_adler32:
            cur_hash = self.hasher.hexdigest()
        else:
            cur_hash = format(self.hasher & 0xFFFFFFF, '08x')
        try:
            if self.hash_dict[file.as_posix()] != cur_hash:
                self.hash_dict[file.as_posix()] = cur_hash
                if self.debug:
                    print(f"File modification detected: [{file}]")
                return True
        except KeyError:
            if self.debug:
                print(f"File hash key does not exist, creating now: [{file.as_posix()}]")
            self.hash_dict[file.as_posix()] = cur_hash
            return True
        del self.hasher
        return False

    def scan_directory(self) -> bool:
        file_modified = False
        source_dir = self.config[MAIN_SETTINGS][SOURCE_DIR]
        for (dir_path, dir_names, file_names) in walk(source_dir, topdown=False):
            print("Synchronization init")

            # Copy source files to replica directory if there's a hash mismatch.
            file_modified = self.copy_file_to_replica(dir_path=dir_path, file_names=file_names)

            # Delete files in replica directory that no longer exist in the source directory.
            self.delete_missing_files(dir_path=dir_path, file_names=file_names)

            print("Synchronization complete")
        return file_modified
