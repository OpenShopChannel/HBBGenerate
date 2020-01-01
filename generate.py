import glob
import json
import lxml.etree as tree
import os
import subprocess
import time
from datetime import datetime

for f in glob.glob("/var/www/openshop/hbb1/public_html/unzipped_apps/*/"):
    app_name = f.replace("/var/www/openshop/hbb1/public_html/unzipped_apps/", "").replace("/", "")
    subprocess.call(["mkdir", "/var/www/openshop/hbb1/public_html/hbb/" + app_name])
    subprocess.call(["7z", "a", "/var/www/openshop/hbb1/public_html/hbb/{}/{}.zip".format(app_name, app_name), f + "*"])
    subprocess.call(["cp", f + "apps/" + app_name + "/icon.png", "/var/www/openshop/hbb1/public_html/hbb/{}.png".format(app_name)])
    subprocess.call(["cp", f + "apps/" + app_name + "/icon.png", "/var/www/openshop/hbb1/public_html/hbb/{}/icon.png".format(app_name)])
    subprocess.call(["7z", "a", "/var/www/openshop/hbb1/public_html/hbb/homebrew_browser/temp_files.zip", "/var/www/openshop/hbb1/public_html/hbb/{}.png".format(app_name)])

metadata = json.loads(open("metadata.json", "r").read())

category = ["Demos", "Emulators", "Games", "Media", "Utilities"]

list = ""
list += "Homebrew 2092896 v0.3.9e | - Updated with latest libogc which should correct network issues some users are experiencing\n"

for c in category:
    for k, v in metadata.items():
        if v[0] == c:
            print(k)
            parser = tree.XMLParser(recover=True)
            xml = tree.parse("unzipped_apps/{}/apps/{}/meta.xml".format(k, k), parser=parser)
            type = ""
            if os.path.exists("unzipped_apps/{}/apps/{}/boot.elf".format(k, k)):
                type = "elf"
            elif os.path.exists("unzipped_apps/{}/apps/{}/boot.dol".format(k, k)):
                type = "dol"
            elif os.path.exists("unzipped_apps/{}/apps/{}/theme.zip".format(k, k)):
                type = "thm"
            short_description = ""
            if v[2] != "":
                short_description = v[2]
            else:
                try:
                    short_description = xml.find("short_description").text
                except:
                    try:
                        short_description = xml.find("long_description").text.strip().split("\n")[0]
                    except:
                        short_description = "No description provided."
            long_description = ""
            if v[3] != "":
                long_description = v[3]
            else:
                try:
                    long_description = xml.find("long_description").text.strip().split("\n")[0]
                except:
                    try:
                        long_description = xml.find("short_description").text
                    except:
                        long_description = "No description provided."
            paths = glob.glob("unzipped_apps/{}/**/".format(k), recursive=True)
            paths.remove("unzipped_apps/{}/".format(k))
            paths.remove("unzipped_apps/{}/apps/".format(k))
            paths.remove("unzipped_apps/{}/apps/{}/".format(k, k))
            for dir in paths:
                paths[paths.index(dir)] = dir.replace("unzipped_apps/{}".format(k), "")
            for dir in paths:
                paths[paths.index(dir)] = dir[:-1]
            path = ";".join(paths) + " . ."
            if path != "":
                path = " " + path
            if xml.find("coder") is not None:
                coder = xml.find("coder").text
            else:
                if xml.find("author") is not None:
                    coder = xml.find("author").text
                else:
                    coder = "Unknown"
            if xml.find("release_date") is not None:
                timestamp = xml.find("release_date").text
                if timestamp is None:
                    timestamp = str(0)
                try:
                    if len(timestamp) == 14:
                        timestamp = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                    elif len(timestamp) == 12:
                        timestamp = datetime.strptime(timestamp, "%Y%m%d%H%M")
                    elif len(timestamp) == 8:
                        timestamp = datetime.strptime(timestamp, "%Y%m%d")
                    timestamp = int(time.mktime(timestamp.timetuple()))
                except:
                    timestamp = str(0)
            else:
                timestamp = str(0)
            list += "{} {} 0 0 {} 0 <*> {}{}\n".format(k, timestamp, type, v[1], path) + \
                    xml.find("name").text + "\n" + \
                    coder + "\n" + \
                    xml.find("version").text + "\n" + \
                    "***" + "\n" + \
                    short_description + "\n" + \
                    long_description + "\n"
            """try:
                print(xml.find("long_description").text.split("\n")[0])
            except:
                try:
                    print(xml.find("short_description").text)
                except:
                    print("No description provided.")"""
    list += "={}=\n".format(c)

txtlist = open("hbblist_internal.txt", "w")
txtlist.write(list)
txtlist.close()

subprocess.call(["php", "list.php"],
                 stdout=subprocess.PIPE)

subprocess.call(["cp", "hbb/listv036.txt", "hbb/homebrew_browser/listv036.txt"],
                 stdout=subprocess.PIPE)
