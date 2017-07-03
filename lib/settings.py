from __future__ import print_function

import logging
import re
import string
import sys
import time
import math

import requests
from colorlog import ColoredFormatter

from lib.algorithms.hashing_algs import *

# Create logging
log_level = logging.DEBUG
logger_format = "[%(log_color)s%(asctime)s %(levelname)s%(reset)s] %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(log_level)
formatter = ColoredFormatter(logger_format, datefmt="%H:%M:%S",
                             log_colors={
                                 "DEBUG": "cyan",
                                 "INFO": "bold,green",
                                 "WARNING": "yellow",
                                 "ERROR": "red",
                                 "CRITICAL": "bold,red"
                             })
stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)
LOGGER = logging.getLogger('configlog')
LOGGER.setLevel(log_level)
LOGGER.addHandler(stream)

# Version number <major>.<minor>.<patch>.<git-commit>
VERSION = "1.10.19.33"
# Colors, green if stable, yellow if dev
TYPE_COLORS = {"dev": 33, "stable": 92}
# Version string, dev or stable release?
if len(VERSION) >= 4:
    VERSION_STRING = "\033[92mv{}\033[0m(\033[{}m\033[1mdev\033[0m)".format(VERSION, TYPE_COLORS["dev"])
else:
    VERSION_STRING = "\033[92mv{}\033[0m(\033[{}m\033[1mstable\033[0m)".format(VERSION, TYPE_COLORS["stable"])
# Program saying
SAYING = "\033[97mAdvanced Hash Manipulation\033[0m"
# Clone link
CLONE = "\033[97mhttps://github.com/ekultek/dagon.git\033[0m"
# Homepage link
HOMEPAGE = "\033[97mhttps://ekultek.github.io/Dagon/\033[0m"
# Issue page
DAGON_ISSUE_LINK = "https://github.com/Ekultek/Dagon/issues/new"
# Sexy banner to display when asked for
BANNER = """\033[91m
'||''|.
 ||   ||   ....    ... .   ...   .. ...
 ||    || '' .||  ||_||  .|  '|.  ||  ||
 ||    || .|' ||   |''   ||   ||  ||  ||
.||...|'  '|..'|' '||||.  '|..|' .||. ||. [][][]
                 .|....'\033[0m
{} ... {}
Clone: {}
Home: {}
""".format(SAYING, VERSION_STRING, CLONE, HOMEPAGE)
# Algorithm function dict
FUNC_DICT = {
    "md2": md2, "md4": md4, "md5": md5, "half md5": half_md5, "md5(md5(pass)+md5(salt))": md5_pass_salt,
    "md5(md5(pass))": md5_md5_pass, "md5(salt+pass+salt)": md5_salt_pass_salt, "md5(md5(md5(pass)))": md5_md5_md5_pass,
    "mysql": mysql_hash, "blowfish": blowfish_hash, "oracle 11g": oracle_11g, "oracle 10g": oracle_10g,
    "mssql 2005": mssql_2005, "postgresql": postgres, "mssql 2000": mssql_2000,
    "ripemd160": ripemd160,
    "blake224": blake224, "blake256": blake256, "blake384": blake384, "blake512": blake512,
    "sha1": sha1, "sha224": sha224, "sha256": sha256, "sha384": sha384, "sha512": sha512,
    "half sha1": half_sha1, "sha1(sha1(pass))": sha1_sha1_pass, "ssha": ssha,
    "sha1(sha1(sha1(pass)))": sha1_sha1_sha1_pass,
    "sha3_224": sha3_224, "sha3_256": sha3_256, "sha3_384": sha3_384, "sha3_512": sha3_512,
    "whirlpool": whirlpool, "crc32": crc32, "ntlm": ntlm, "windows local (ntlm)": ntlm, "crc64": crc64,
    "tiger192": tiger192
}
# Identity numbers
IDENTIFICATION = {
    # MD indicators
    100: "md5", 110: "md2", 120: "md4",
    # MD special indicators
    130: "md5(md5(pass)+md5(salt))", 131: "md5(md5(pass))", 132: "half md5",
    133: "md5(salt+pass+salt)", 134: "md5(md5(md5(pass)))",

    # Blake indicators
    200: "blake224", 210: "blake256", 220: "blake384", 230: "blake512",

    # SHA indicators
    300: "sha1", 310: "sha224", 320: "sha256", 330: "sha384", 340: "sha512",
    400: "sha3_224", 410: "sha3_256", 420: "sha3_384", 430: "sha3_512",
    # SHA special indicators
    351: "half sha1", 352: "sha1(sha1(pass))", 353: "ssha", 354: "sha1(sha1(sha1(pass)))",

    # Database and external hash indicators
    500: "blowfish", 510: "mysql", 520: "oracle 11g", 530: "oracle 10g", 540: "mssql 2005", 550: "postgresql",
    560: "mssql 2000",

    # Ripemd indicators
    600: "ripemd160",

    # Tiger indicators
    700: "tiger192",

    # Other
    800: "whirlpool", 900: "crc32", 1000: "ntlm", 1100: "crc64"
}
# Regular expression to see if you already have a bruteforce wordlist created
WORDLIST_RE = re.compile("Dagon-bfdict-[a-zA-Z]{7}.txt")
# Wordlist links
WORDLIST_LINKS = [
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrL2FhODgyMDk5ZWQxYzNlZjAwNWYzYWY2ZjhmYmFhZTExL3Jhdy84ODQ4NjBhNjAzZWQ0MjE3MTgyN2E1MmE3M2VjNzAzMjNhOGExZWY5L2dpc3RmaWxlMS50eHQ=',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzAwNWU3OWQ2NmU2MzA2YWI0MzZjOGJmYTc1ZTRiODMwL3Jhdy8xNjY5YjNjMDFmMjRhM2Q2OTMwZDNmNDE1Mjk3ZTg5OGQ1YjY2NGUzL29wZW53YWxsXzMudHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzE4NTBmM2EwZGNjNDE0YWZlOGM3NjYyMjBlOTYxYjE4L3Jhdy9iYWQ0NTA0NjcwY2FmM2UxNDY1NWI2ZjJlZGQ0MjJmOTJjMzI2MWI5L215c3BhY2UudHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzBkYWU2YTI5MjgzMjcyNmE2Y2MyN2VlNmVjOTdmMTFjL3Jhdy84MWFkOWFkOWUwZjQxMmY2YjIwMTM3MDI2NDcxZGRmNDJlN2JjMjkyL2pvaG4udHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrL2Q4ZjZiYjE2MGEzYzY2YzgyNWEwYWY0NDdhMDM1MDVhL3Jhdy83MWI4NmM5MGU3NDRkZjM0YzY3ODFjM2U0MmFjMThkOGM4ZjdkYjNlL2NhaW4udHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrL2JmM2MwYjQwMTVlYzlkMzY4YzBlNTczNzQ0MTAzYmU1L3Jhdy9lNzBhMThmOTUwNGYwZmMyYjRhMWRmN2M0Mjg2YjcyOWUyMzQ5ODljL29wZW53YWxsXzIudHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzQ1ZTExZDBhMzNjZGE1YjM3NDM5OGYyMDgxYjEwZWZiL3Jhdy8wNzQ1ZGMzNjFlZDU5NjJiMjNkYjUxM2FkOWQyOTNlODk0YjI0YTY0L2RjLnR4dA==',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzNmMzcxMWUzMDdlOGM0ZTM0MDkzYzI1OGFkN2UzZWZkL3Jhdy9hMjNiYmM3YTgxNTZhOGU5NTU3NmViYTA3MmIwZDg4ZTJmYjk1MzZiL2dtYWlsXzIudHh0',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrL2U3MzE4MGM3MGZmMzY3NDFhM2M4NzIzMDZiNTFhOTU1L3Jhdy9jODE0YjFjOTZiNGJkYzZlYTRlZDE3MmMzNDIwOTg2NTBjOTcyYWZjL2J0NC50eHQ=',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2JlcnplcmswL1Byb2JhYmxlLVdvcmRsaXN0cy9tYXN0ZXIvRGljdGlvbmFyeS1TdHlsZS9NYWluRW5nbGlzaERpY3Rpb25hcnkudHh0',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvdHdpdHRlci1iYW5uZWQudHh0',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvdHVzY2wudHh0',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvMTBfbWlsbGlvbl9wYXNzd29yZF9saXN0X3RvcF8xMDAwMDAwLnR4dA==',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvTGl6YXJkX1NxdWFkLnR4dA==',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrLzZjNTEzNzdhMzM5YzM4YTdiMDIwMjc3NGYyOWQ5MWUyL3Jhdy82MWM1Y2I2NWNkMTljMmI4YjNkYmY4N2EzOTFkN2NkNzcxYjZjZTljL2V4YW1wbGUuZGljdA==',
    'aHR0cHM6Ly9naXN0LmdpdGh1YnVzZXJjb250ZW50LmNvbS9Fa3VsdGVrL2Q0ODc4NWNhODAxMjcwZjc3MzI3NzY1ZDI0Y2Y2MWM4L3Jhdy9iOTg3N2ZjYmVhZGEyMjNjM2I1ZmRhMGJmNWI4YmFiMzBmNmNhNGE0L2dkaWN0LnR4dA==',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvMTBfbWlsbGlvbl9wYXNzd29yZF9saXN0X3RvcF8xMDAwMDAwLnR4dA==',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvTW9zdFBvcHVsYXJMZXR0ZXJQYXNzZXMudHh0',
    'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2RhbmllbG1pZXNzbGVyL1NlY0xpc3RzL21hc3Rlci9QYXNzd29yZHMvS2V5Ym9hcmRDb21iaW5hdGlvbnMudHh0'
]


def start_up(verbose=False):
    """ Start the application """
    if not verbose:
        print("\n[*] Starting up at {}..\n".format(time.strftime("%H:%M:%S")))
    else:
        print("[*] Starting up at: {}..\n".format(str(time.time())))


def shutdown(exit_key=0, verbose=False):
    """ Shut down the application """
    if not verbose:
        print('\n[*] Shutting down at {}..\n'.format(time.strftime("%H:%M:%S")))
        exit(exit_key)
    else:
        print("\n[*] Shutting down at {}..\n".format(str(time.time())))
        exit(exit_key)


def convert_file_size(byte_size, magic_num=1024):
    """
      Convert a integer to a file size (B, KB, MB, etc..)
      > :param byte_size: integer that is the amount of data in bytes
      > :param magic_num: the magic number that makes everything work, 1024
      > :return: the amount of data in bytes, kilobytes, megabytes, etc..
    """
    if byte_size == 0:
        return "0B"
    # Probably won't need more then GB, but still it's good to have
    size_data_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    floored = int(math.floor(math.log(byte_size, magic_num)))
    pow_data = math.pow(magic_num, floored)
    rounded_data = round(byte_size / pow_data, 2)
    return "{}{}".format(rounded_data, size_data_names[floored])


def verify_python_version(verbose=False):  # and we're back :|
    """
      Verify python version
    """
    if verbose:
        LOGGER.debug("Verifying what version of Python you have..")
    current_py_version = sys.version.split(" ")[0]
    if "2.7" not in current_py_version:
        LOGGER.debug("This application requires python 2.7.x to run.. "
                     "You currently have python version {} installed..".format(current_py_version))


def show_banner():
    """
      Show the banner of the program

      > :return: banner
    """
    print(BANNER)


def show_hidden_banner():
    """
      Show the hidden banner (just saying and clone)

      > :return: a hidden banner
    """
    print("Dagon .. {} {}\nClone: {}\n".format(SAYING, VERSION_STRING, CLONE))


def prompt(question, choices):
    """
      Create a prompt for the user

      > :param question: a string containing the question needed to be answered
      > :param choices: a string containing choices
      > :return: a prompt
    """
    try:
        return raw_input("[{} PROMPT] {}[{}]: ".format(time.strftime("%H:%M:%S"), question, choices))
    except:  # idk what the exception is, so if you know it lemme know
        return input("[{} PROMPT] {}[{}]: ".format(time.strftime("%H:%M:%S"), question, choices))


def download_rand_wordlist(verbose=False, multi=1):
    """
      Download a random wordlist from some wordlists I have laying around

      > :param b64link: a base64 encoded wordlist link
    """
    if multi == 1:
        b64link = random.choice(WORDLIST_LINKS)
        filename = "Download-" + random_salt_generator(use_string=True)[0]
        LOGGER.info("Beginning download..")
        with open("{}.txt".format(filename), "a+") as wordlist:
            response = requests.get(base64.b64decode(b64link), stream=True)
            total_length = response.headers.get('content-length')
            if verbose:
                LOGGER.debug("Content length to be downloaded: {}..".format(convert_file_size(int(total_length))))
                LOGGER.debug("Wordlist link downloading from: '{}'..".format(b64link))
            if total_length is None:
                wordlist.write(response.content)
            else:
                start = time.time()
                if verbose:
                    LOGGER.debug("Starting download at {}..".format(start))
                downloaded = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=1024):
                    downloaded += len(data)
                    wordlist.write(data)
                    done = int(50 * downloaded / total_length)
                    sys.stdout.write("\r[\033[93m{}\033[0m{}]".format("#" * done, " " * (50-done)))
                    sys.stdout.flush()
        print("")
        LOGGER.info("Download complete, saved under: {}.txt. Time elapsed: {}s".format(filename, time.time() - start))
    else:
        if multi <= len(WORDLIST_LINKS):
            for _ in range(int(multi)):
                LOGGER.info("Downloading wordlist #{}..".format(_ + 1))
                download_rand_wordlist(verbose=verbose)
        else:
            LOGGER.fatal(
                "There are currently {} wordlists available for download, and you "
                "have chose to download {}. Seeing as there aren't that many right now "
                "this download will fail, try again with a smaller number..".format(len(WORDLIST_LINKS), multi)
            )


def random_salt_generator(use_string=False, use_number=False, length=None, warning=True):
    """
      Create a random string of salt to append to the beginning of a hash

      Example:
        >>> random_salt_generator(use_string=True)
        fUFVsatp
    """
    try:
        salt_length = int(length)
    except TypeError:
        salt_length = 8  # default to 8 if length is None
    except ValueError:
        raise ValueError('length must be an integer!')  # default to 8 again???

    char_set = ''
    salt_type = []
    if use_string:
        char_set += string.ascii_letters
        salt_type.append('characters')
    if use_number:
        char_set += string.digits
        salt_type.append('integers')
    if not salt_type:
        # if both `use_string` & `use_number` are False, default to digits
        if warning:
            LOGGER.warning("No choice given as salt, defaulting to numbers..")
        char_set = string.digits
        salt_type.append('integers')

    if salt_length >= 12:
        LOGGER.warning(
            "It is recommended to keep salt length under 12 {} for faster hashing..".format(
                ' and '.join(salt_type)))

    salt = ''.join(random.choice(char_set) for _ in range(salt_length))
    placement = random.choice(("front", "back"))
    return salt, placement


def match_found(data_tuple, data_sep="-" * 75, item_found="+", least_likely="-", kind="cracked", all_types=False):
    """
      Create a banner for finding a match

      > :param data_tuple: tuple containing the information required
      > :param data_sep: what to separate the information with
      > :param item_found: makes it look pretty for the items
      > :param least_likely: makes more pretty formatting for least likely hashes
    """
    if data_tuple is None:
        no_alg_err = (
            "It appears that no algorithm that can match this hash has "
            "been implemented yet. If you feel that this is wrong, "
            "please make a issue regarding this, and we'll see if we "
            "can get it implemented.")
        LOGGER.fatal(no_alg_err)
        shutdown(1)
    if data_tuple[0][1] is None and all_types:
        LOGGER.warning("Only one possible type found for given hash..")
    sort_cracked = ["Clear Text: ", "Hash: ", "Tries attempted: ", "Algorithm Used: "]
    if kind == "cracked":
        print(data_sep + "\n" + "[{}] Match found:\n".format(item_found) + data_sep)
        for i, item in enumerate(sort_cracked):
            print("[{}] {}{}".format(item_found, item, data_tuple[i].upper() if i == 3 else data_tuple[i]))
        print(data_sep)
    else:
        if all_types:
            data_tuple = data_tuple[0] + data_tuple[1]
            print(data_sep + "\n" + "[{}] Most Likely Hash Type(s):\n".format(item_found) + data_sep)
            for i, _ in enumerate(data_tuple):
                if i <= 2:
                    if _ is not None:
                        print("[{}] {}".format(item_found, data_tuple[i].upper()))
                        if i == 2:
                            print(data_sep + "\n" +
                                  "[{}] Least Likely Hash Type(s)(possibly not implemented):\n".format(
                                      least_likely) + data_sep)
                else:
                    if _ is not None:
                        print("[{}] {} {}".format(least_likely, data_tuple[i].upper(), "(not implemented yet)" if _ not in FUNC_DICT.keys() else ""))

            print(data_sep)
        else:
            print(data_sep + "\n" + "[{}] Most Likely Hash Types:\n".format(item_found) + data_sep)
            for i, _ in enumerate(data_tuple):
                if i <= 2:
                    if _ is not None:
                        print("[{}] {}".format(item_found, data_tuple[i].upper()))
            print(data_sep)


def update_system():
    """ Update Dagon to the newest development version """
    import subprocess
    updater = subprocess.check_output("git pull origin master")
    if "Already up-to-date." in updater:
        return 1
    elif "error" or "Error" in updater:
        return -1
    else:
        return 0


def show_available_algs(show_all=False, supp="+", not_yet="-", spacer1=" "*5, spacer2=" "*3):
    """ Show all algorithms available in the program """
    being_worked_on = [
        "wordpress", "scrypt", "sha2",
        "dsa", "haval160", "tiger160"
    ]
    misc_info_msg = (
        "There are currently {} supported algorithms in Dagon. To "
        "suggest the creation of a new algorithm please go make an "
        "issue here {}")
    LOGGER.info(misc_info_msg.format(len(IDENTIFICATION), DAGON_ISSUE_LINK))
    print("\n{space1}ID#{space2}Alg:\n{space1}---{space2}----".format(space1=spacer1, space2=spacer2))
    for item in sorted(IDENTIFICATION.keys()):
        print("\033[94m[{}]\033[0m  {}   {}".format(supp, item, IDENTIFICATION[item].upper()))
    if show_all:
        print("\nNot implemented yet:")
        for item in sorted(being_worked_on):
            print("\033[91m[{}]\033[0m {}".format(not_yet, item.upper()))


def algorithm_pointers(pointer_identity):
    """ Point to the correct algorithm given by an identification number """
    try:
        return IDENTIFICATION[int(pointer_identity)]
    except TypeError:
        return None
    except (KeyError, ValueError):
        LOGGER.fatal("The algorithm identification number you have specified is invalid.")
        LOGGER.debug("Valid identification numbers are: {}".format(IDENTIFICATION))


def integrity_check(url="https://raw.githubusercontent.com/Ekultek/Dagon/master/md5sum/checksum.md5",
                    path="{}/md5sum/checksum.md5"):
    """ Check the integrity of the program """
    LOGGER.info("Checking program integrity...")
    if open(path.format(os.getcwd())).read() != requests.get(url).text:
        checksum_fail = (
            "MD5 sums did not match from origin master, integrity check"
            " has failed, this could be because there is a new version "
            "available. Please check for a new version and download "
            "that ({}), or be sure that you have not changed any of the"
            " applications code.")
        LOGGER.fatal(checksum_fail.format("https://github.com/ekultek/dagon.git"))
        shutdown(-1)
