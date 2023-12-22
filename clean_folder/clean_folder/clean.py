import re
import sys
import shutil
from pathlib import Path


UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}

images = list()   #('JPEG', 'PNG', 'JPG', 'SVG');
video = list()    #('AVI', 'MP4', 'MOV', 'MKV');
documents = list()     #('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX');
audio = list()    #('MP3', 'OGG', 'WAV', 'AMR');
archives = list() #('ZIP', 'GZ', 'TAR');
others = list()
folders = list()
unknown = set()
extensions = set()

registered_extensions = {
    'images': images,
    'video': video,
    'documents': documents,
    'audio': audio,
    'archives': archives,
    'others': others
}


for key, value in zip(UKRAINIAN_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('images', 'video', 'documents', 'audio', 'archives', 'others'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            if extension in ['JPEG', 'PNG', 'JPG', 'SVG']:
                    new_extension = 'images'
                    container = registered_extensions[new_extension]
                    extensions.add(extension)
                    container.append(new_name)
            if extension in ['AVI', 'MP4', 'MOV', 'MKV']:
                    new_extension = 'video'
                    container = registered_extensions[new_extension]
                    extensions.add(extension)
                    container.append(new_name)
            if extension in ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']:
                    new_extension = 'documents'
                    container = registered_extensions[new_extension]
                    extensions.add(extension)
                    container.append(new_name)
            if extension in ['MP3', 'OGG', 'WAV', 'AMR']:
                    new_extension = 'audio'
                    container = registered_extensions[new_extension]
                    extensions.add(extension)
                    container.append(new_name)
            if extension in ['ZIP', 'GZ', 'TAR']:
                    new_extension = 'archives'
                    container = registered_extensions[new_extension]
                    extensions.add(extension)
                    container.append(new_name)
            if extension not in ['JPEG', 'PNG', 'JPG', 'SVG', 'AVI', 'MP4', 'MOV', 'MKV', 'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'MP3', 'OGG', 'WAV', 'AMR', 'ZIP', 'GZ', 'TAR']:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name)
    new_name = re.sub(r'.zip|.gz|.tar', '', new_name)

    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
    except FileNotFoundError:
        archive_folder.rmdir()
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def remove_unarchived_file(path):
    for item in path.iterdir():
        if item.is_file():
            try:
                item.unlink()
            except OSError:
                pass


def main():
    folder_path = Path(sys.argv[1])
    scan(folder_path)

    for key, value in registered_extensions.items():
        for file in value:
            if key == "archives":
                handle_archive(file, folder_path, "archives")
            else:
                handle_file(file, folder_path, key)

    remove_empty_folders(folder_path)
    remove_unarchived_file(folder_path)

if __name__ == '__main__':
    main()