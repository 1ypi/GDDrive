#!/usr/bin/env python3

import base64, gzip, requests, hashlib, base64, json, random, string, zlib, os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
INDEX_PATH = BASE_DIR / "index.json"
DOWNLOADS_DIR = BASE_DIR / "Downloads"

def log(message, level, function=""):
    now = datetime.now()

    if function != "":
        if level == 0:
            print(f"[{now.strftime('%H:%M:%S')}] {function}: " + message)
        elif level == 1:
            print(f"[{now.strftime('%H:%M:%S')}] [WARNING] {function}: " + message)
        elif level == 2:
            print(f"[{now.strftime('%H:%M:%S')}] [ERROR] {function}: " + message)
    else:
        if level == 0:
            print(f"[{now.strftime('%H:%M:%S')}] " + message)
        elif level == 1:
            print(f"[{now.strftime('%H:%M:%S')}] [WARNING] " + message)
        elif level == 2:
            print(f"[{now.strftime('%H:%M:%S')}] [ERROR] " + message)

def normalize_index_key(path: str) -> str:
    return os.path.basename(os.path.normpath(path.strip()))

def ensure_storage_paths():
    DOWNLOADS_DIR.mkdir(exist_ok=True)

    if not CREDENTIALS_PATH.exists():
        with CREDENTIALS_PATH.open("w", encoding="utf-8") as credentials_file:
            json.dump({}, credentials_file)

    if not INDEX_PATH.exists():
        with INDEX_PATH.open("w", encoding="utf-8") as index_file:
            json.dump({}, index_file)

headers = {
    "User-Agent": ""
}

characters = string.ascii_letters + string.digits
start_of_level = "kS38,1_40_2_125_3_255_11_255_12_255_13_255_4_-1_6_1000_7_1_15_1_18_0_8_1|1_0_2_102_3_255_11_255_12_255_13_255_4_-1_6_1001_7_1_15_1_18_0_8_1|1_0_2_102_3_255_11_255_12_255_13_255_4_-1_6_1009_7_1_15_1_18_0_8_1|1_255_2_255_3_255_11_255_12_255_13_255_4_-1_6_1002_5_1_7_1_15_1_18_0_8_1|1_40_2_125_3_255_11_255_12_255_13_255_4_-1_6_1013_7_1_15_1_18_0_8_1|1_40_2_125_3_255_11_255_12_255_13_255_4_-1_6_1014_7_1_15_1_18_0_8_1|1_0_2_200_3_255_11_255_12_255_13_255_4_-1_6_1005_5_1_7_1_15_1_18_0_8_1|1_0_2_125_3_255_11_255_12_255_13_255_4_-1_6_1006_5_1_7_1_15_1_18_0_8_1|,kA13,0,kA15,0,kA16,0,kA14,,kA6,0,kA7,0,kA25,0,kA17,0,kA18,0,kS39,0,kA2,0,kA3,0,kA8,0,kA4,0,kA9,0,kA10,0,kA22,0,kA23,0,kA24,0,kA27,1,kA40,1,kA48,1,kA41,1,kA42,1,kA28,0,kA29,0,kA31,1,kA32,1,kA36,0,kA43,0,kA44,0,kA45,1,kA46,0,kA47,0,kA33,1,kA34,1,kA35,0,kA37,1,kA38,1,kA39,1,kA19,0,kA26,0,kA20,0,kA21,0,kA11,0;"


used_keys = [1, 6, 7, 8, 9, 10, 12, 20, 21, 22, 23, 24, 25, 28, 29, 33, 34, 45, 46, 47, 50, 51, 54, 61, 63, 68, 69, 71, 72, 73, 75, 76, 77, 80, 84, 85, 90, 91, 92, 95, 97, 105, 107, 108, 113, 114, 115]

def xor_cipher(text, key):
    result = []

    for i, ch in enumerate(text):
        byte = ord(ch)
        x_key = ord(key[i % len(key)])
        result.append(chr(byte ^ x_key))

    return "".join(result)

def generate_gjp2(password: str = "", salt: str = "mI29fmAnxgTs") -> str:
    password += salt
    hash = hashlib.sha1(password.encode()).hexdigest()

    return hash

def generate_chk(values: [int, str] = [], key: str = "", salt: str = "") -> str:
    values.append(salt)

    string = ("").join(map(str, values))

    hashed = hashlib.sha1(string.encode()).hexdigest()
    xored = xor_cipher(hashed, key)
    final = base64.urlsafe_b64encode(xored.encode()).decode()

    return final

def generate_upload_seed(data: str, chars: int = 50) -> str:
    if len(data) < chars:
        return data
    step = len(data) // chars
    return data[::step][:chars]

def parse_level(level_string: str):
    file_bytes = bytearray()

    level_objects = level_string.split(";")[1:]

    for object in level_objects:
        split_object = object.split(",")

        for i in range(0, len(split_object), 2):
            try:
                if int(split_object[i]) in used_keys:
                    if int(split_object[i]) != 1:
                        if int(split_object[i + 1]) > 255:
                            file_bytes.append(255)
                        elif int(split_object[i + 1]) < 0:
                            file_bytes.append(0)
                        else:
                            if i + 1 >= len(split_object):
                                continue

                            file_bytes.append(int(split_object[i + 1]))
                    else:
                        if int(split_object[i + 1]) > 255:
                            file_bytes.append(255)
                        elif int(split_object[i + 1]) < 0:
                            file_bytes.append(0)
                        else:
                            if i + 1 >= len(split_object):
                                continue
                            
                            file_bytes.append(int(split_object[i + 1]) - 1)
            except:
                continue
    
    return file_bytes

def make_level(file_bytes: bytearray):
    current_x = 0
    current_y = 500

    i = 1

    key_on = 1
    current_object = "1," + str(file_bytes[0] + 1) + ",2,0,3,500,"
    level_string = ""
    object_count = 1

    while i != len(file_bytes) and not i > len(file_bytes):
        current_object += str(used_keys[key_on]) + "," + str(file_bytes[i])
        
        key_on += 1
        
        if key_on == len(used_keys):
            key_on = 1

            i += 1
            level_string += current_object + ";"
            current_y -= 30

            if current_y < 0:
                current_y = 500
                current_x += 30
            
            if i + 1 >= len(file_bytes):
                continue
            
            current_object = "1," + str(file_bytes[i] + 1) + ",2," + str(current_x) + ",3," + str(current_y) + ","
            object_count += 1
        else:
            current_object += (",")

        i += 1
    
    level_string += current_object + ";"
    object_count += 1

    return start_of_level + level_string, object_count

def encode_level(level_string: str, is_official_level: bool) -> str:
    gzipped = gzip.compress(level_string.encode())
    base64_encoded = base64.urlsafe_b64encode(gzipped)

    if is_official_level:
        base64_encoded = base64_encoded[13:]
    
    return base64_encoded.decode()

def decode_level(level_data: str, is_official_level: bool) -> str:
    if is_official_level:
        level_data = 'H4sIAAAAAAAAA' + level_data
    
    base64_decoded = base64.urlsafe_b64decode(level_data.encode())
    decompressed = zlib.decompress(base64_decoded, 15 | 32)

    return decompressed.decode()

def detect_file_extension(file_bytes: bytes):
    file_bytes = bytes(file_bytes)

    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png", "PNG image"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return ".jpg", "JPEG image"
    if file_bytes.startswith((b"GIF87a", b"GIF89a")):
        return ".gif", "GIF image"
    if file_bytes.startswith(b"BM"):
        return ".bmp", "BMP image"
    if file_bytes.startswith((b"II*\x00", b"MM\x00*")):
        return ".tiff", "TIFF image"
    if file_bytes.startswith(b"\x00\x00\x01\x00"):
        return ".ico", "ICO image"
    if len(file_bytes) >= 12 and file_bytes[0:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return ".webp", "WebP image"
    if len(file_bytes) >= 12 and file_bytes[4:8] == b"ftyp":
        brand = file_bytes[8:12]

        if brand in {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1"}:
            return ".heic", "HEIC image"
        if brand in {b"qt  "}:
            return ".mov", "MOV video"
        if brand in {b"mp41", b"mp42", b"isom", b"iso2", b"avc1", b"dash", b"MSNV"}:
            return ".mp4", "MP4 video"
        if brand in {b"M4V ", b"m4v "}:
            return ".m4v", "M4V video"
        if brand in {b"3gp4", b"3gp5", b"3gp6", b"3gg6", b"3g2a", b"3g2b", b"3ge6"}:
            return ".3gp", "3GP video"
    if file_bytes.startswith(b"\x1a\x45\xdf\xa3"):
        return ".mkv", "Matroska video"
    if file_bytes.startswith(b"RIFF") and len(file_bytes) >= 12 and file_bytes[8:12] == b"AVI ":
        return ".avi", "AVI video"
    if file_bytes.startswith(b"\x30\x26\xb2\x75\x8e\x66\xcf\x11"):
        return ".wmv", "WMV video"
    if file_bytes.startswith(b"FLV"):
        return ".flv", "FLV video"

    return "", "unknown file type"

def choose_output_filename(filename: str, file_bytes: bytes):
    detected_extension, detected_description = detect_file_extension(file_bytes)

    if detected_extension == "":
        return filename, detected_description

    base_name, current_extension = os.path.splitext(filename)

    if current_extension.lower() in {"", ".bin"}:
        return base_name + detected_extension, detected_description

    return filename, detected_description

def downloadLevel(id: int) -> str:
    request_data = {
        "levelID": id,
        "secret": "Wmfd2893gb7"
    }

    req = requests.post(url="https://www.boomlings.com/database/downloadGJLevel22.php", data=request_data, headers=headers)

    split_res = req.text.split("#")
    split_res2 = split_res[0].split(":")

    level_string = ""

    for i in range(0, len(split_res2), 2):
        if split_res2[i] == "4":
            level_string = split_res2[i + 1]
            break
    
    if level_string == "":
        log("Level " + str(id) + " not found!", 2)
        return ""
    else:
        log("Downloaded level " + str(id) + "!", 0)

        return decode_level(level_string, False)

def resolve_download_target(download_target: str, index_data: dict):
    normalized_target = normalize_index_key(download_target)

    if normalized_target in index_data:
        return index_data[normalized_target]["level_id"], normalized_target

    stripped_target = download_target.strip()

    if stripped_target.isdigit():
        level_id = int(stripped_target)
        return level_id, "level_" + str(level_id) + ".bin"

    return None, None

def deleteLevel(id: int):
    request_data = {
        "accountID": account_id,
        "gjp2": gjp_2,
        "levelID": id,
        "secret": "Wmfv2898gc9"
    }

    req = requests.post(url="https://www.boomlings.com/database/deleteGJLevelUser20.php", data=request_data, headers=headers)

    if req.text != "-1":
        log("Level ID " + str(id) + " deleted successfully!", 0)
        return 0
    else:
        log("Could not delete level ID " + str(id) + "!", 2)
        return 1

def prompt_login_credentials():
    print("To begin, please log in to Geometry Dash.")
    username = input(" - Username: ").strip()
    password = input(" - Password: ")
    account_id = input(" - Account ID: ").strip()

    log("Generating GJP2...", 0)
    gjp_2 = generate_gjp2(password)

    return username, gjp_2, account_id

def save_credentials(username: str, gjp_2: str, account_id: str):
    log("Storing credentials...", 0)
    with CREDENTIALS_PATH.open("w", encoding="utf-8") as credentials_file_write:
        data = {
            "gjp2": gjp_2,
            "username": username,
            "account_id": account_id
        }

        json.dump(data, credentials_file_write)

def load_credentials():
    ensure_storage_paths()

    if CREDENTIALS_PATH.exists():
        with CREDENTIALS_PATH.open("r", encoding="utf-8") as credentials_file:
            data = json.load(credentials_file)

        if "gjp2" in data and "username" in data and "account_id" in data:
            log("Credentials saved, skipping login...", 0)
            return data["username"], data["gjp2"], data["account_id"]

    username, gjp_2, account_id = prompt_login_credentials()
    save_credentials(username, gjp_2, account_id)
    return username, gjp_2, account_id

def load_index():
    log("Loading file index...", 0)
    ensure_storage_paths()

    with INDEX_PATH.open("r", encoding="utf-8") as index_file:
        return json.load(index_file)

def save_index(index_data: dict):
    with INDEX_PATH.open("w", encoding="utf-8") as index_file:
        json.dump(index_data, index_file)

def main():
    global username, gjp_2, account_id

    print("Welcome to GDDrive!")
    username, gjp_2, account_id = load_credentials()
    index_data = load_index()

    while True:
        print("\nWhat would you like to do?")
        print(" 1 | View files")
        print(" 2 | Upload files")
        print(" 3 | Delete files")
        print(" 4 | Download files")
        print(" 5 | Relogin")
        print(" 6 | Exit\n")

        x = input("Enter your response: ").strip()

        if x == "5":
            username, gjp_2, account_id = prompt_login_credentials()
            save_credentials(username, gjp_2, account_id)
            log("Credentials updated successfully!", 0)
        elif x == "6":
            return
        elif x == "4":
            file_to_download = input("\nPlease provide the file you want to download: ")

            level_id, filename = resolve_download_target(file_to_download, index_data)

            if level_id is None:
                log("That file is not in the index and the input is not a valid level ID.", 2)
                continue

            level_string = downloadLevel(level_id)

            if level_string == "":
                continue
            
            file_bytes = parse_level(level_string)
            filename, detected_description = choose_output_filename(filename, file_bytes)

            DOWNLOADS_DIR.mkdir(exist_ok=True)
            output_path = DOWNLOADS_DIR / filename

            with output_path.open("wb") as downloaded_file:
                downloaded_file.write(file_bytes)
                downloaded_file.flush()

            log("Detected " + detected_description + ".", 0)
            log("Saved extracted file to " + str(output_path), 0)
        elif x == "1":
            print(str(len(index_data)) + " file(s):")
            
            for file in index_data:
                print(" - " + file + " (ID: " + str(index_data[file]["level_id"]) + ")")
        elif x == "3":
            file_to_delete = normalize_index_key(input("\nPlease provide the file you want to delete: "))

            if file_to_delete not in index_data:
                log("That file is not in the index.", 2)
                continue

            success = deleteLevel(index_data[file_to_delete]["level_id"])

            if success == 0:
                del index_data[file_to_delete]
                save_index(index_data)
            else:
                continue

        elif x == "2":
            path_input = input("\nPlease provide the file you want to upload: ").strip()
            input_path = Path(path_input).expanduser()

            if not input_path.is_absolute():
                input_path = (Path.cwd() / input_path).resolve()

            if not input_path.is_file():
                log("That file does not exist.", 2)
                continue

            log("Uploading level...", 0)

            with input_path.open("rb") as uploaded_file:
                level_string, object_count = make_level(uploaded_file.read())
                level_string = encode_level(level_string, False)

                index_key = normalize_index_key(input_path.name)

                if index_key not in index_data:
                    level_name = ''.join(random.choices(characters, k=20))
                else:
                    level_name = index_data[index_key]["level_name"]

                data = {
                    "gameVersion": 22,
                    "binaryVersion": 47,
                    "accountID": account_id,
                    "gjp2": gjp_2,
                    "userName": username,
                    "levelID": 0,
                    "levelName": level_name,
                    "levelDesc": "",
                    "levelVersion": 999,
                    "levelLength": 0,
                    "audioTrack": 0,
                    "auto": 0,
                    "password": 1,
                    "original": 0,
                    "twoPlayer": 0,
                    "songID": 645828,
                    "objects": object_count,
                    "coins": 0,
                    "requestedStars": 10,
                    "unlisted": 2,
                    "ldm": 0,
                    "levelString": level_string,
                    "seed2": generate_chk(key="41274", values=[generate_upload_seed(level_string)], salt="xI25fpAapCQg"),
                    "secret": "Wmfd2893gb7",
                    "dvs": 3
                }

                req = requests.post(url="https://www.boomlings.com/database/uploadGJLevel21.php", data=data, headers=headers)

                if req.text != "-1":
                    log("Level successfully uploaded! ID: " + req.text, 0)
                    log("Adding level to index...", 0)

                    index_data[index_key] = {"level_id": int(req.text), "level_name": level_name}
                    save_index(index_data)

                else:
                    log("Failed to upload level! Maybe your username or password are incorrect? Try to relogin.", 2)
                    continue

if __name__ == "__main__":
    main()
