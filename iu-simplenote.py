#!/usr/bin/python
import sys
import os
import urllib3

SIMPLENOTE_PACKAGE_FILE = "resources/app/package.json"
TEMP_FOLDER = "/tmp"
TAR_GZ_EXT = ".tar.gz"

def main(args):
    import getopt

    print("Simplenote - install || update script")
    simpleNoteLocation = ''

    try:
        opts, args = getopt.getopt(args, "hl:", ["location="])
    except getopt.GetoptError as e:
        print("argument parsing error: {0}".format(e))
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("\nHelp:")
            print("-l, --location => Location where Simplenote (should) reside.\n")
            sys.exit()

        elif opt in ("-l", "--location"):
            simpleNoteLocation = arg

    if not simpleNoteLocation:
        print("unknown Simplenote location")
        sys.exit(3)

    updateOrInstall(simpleNoteLocation)

def updateOrInstall(location):
    import shutil
    import json

    packageFileLocation = os.path.join(location, SIMPLENOTE_PACKAGE_FILE)
    
    try:
        version = json.load(open(packageFileLocation))["version"]
        print("currently installed Simplenote version: {0}".format(version))
        print("=== Starting update ===")
    except FileNotFoundError:
        version = "0.0.1"
        print("Simplenote is not installed in the entered path: {0}.".format(location))
        print("=== Starting installation ===")

    updateInfo = checkUpdates(sys.platform, version)

    if not updateInfo:
        # simplenote update not available
        print("there's no update available at this moment")
        sys.exit()
    else:
        # simplenote update available
        updateInfo = json.loads(updateInfo)
        print("Simplenote version to install: {0}".format(updateInfo["version"]))

        # url is set to tar.gz file (not to .deb)
        url = os.path.splitext(updateInfo["url"])[0] + TAR_GZ_EXT
        downloadAbsolutePath = os.path.join(TEMP_FOLDER ,updateInfo["name"] + TAR_GZ_EXT)

        extractedLocation = downloadAndExtract(url, downloadAbsolutePath)

        # remove old if exist
        if os.path.isdir(location):
            print("removing old version of Simplenote...")
            shutil.rmtree(location)

        # copy new
        print("installing new version of Simplenote")
        shutil.move(extractedLocation, location)

        print("removing temporary files")
        os.remove(downloadAbsolutePath)

        print("installation complete.")
        sys.exit()

def downloadAndExtract(url, downloadAbsolutePath):
    import tarfile
    import certifi

    #download and save data (via streaming)
    print("downloading new version to the location {0}".format(downloadAbsolutePath))
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    req = http.request("GET", url, preload_content=False)
    with open(downloadAbsolutePath, "wb") as out:
        while True:
            data = req.read(1024)
            if not data:
                print("downloading complete")
                break
            out.write(data)
    req.release_conn()

    # decompress file

    print("extracting")
    dec = tarfile.open(downloadAbsolutePath)
    update = os.path.join(TEMP_FOLDER, dec.getnames()[0])
    dec.extractall(TEMP_FOLDER)
    dec.close()
    print("extracting complete")

    return update


def checkUpdates(platform, version):
    import certifi

    print("Checking for newest version...")
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    reqUrl = ("https://app.simplenote.com/desktop/%(platform)s/version?compare=%(version)s" % locals())
    return http.request("GET", reqUrl).data
    

if __name__ == "__main__":
    main(sys.argv[1:])