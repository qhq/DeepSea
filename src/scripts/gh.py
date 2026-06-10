
from pathlib import Path
from github import Github
import urllib.request
import re
import datetime

class GH():
    def __init__(self, ghToken):
        self.token = ghToken
        self.github = Github(self.token)
        
    def formatGMTime(self, timestamp):
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        local_time = datetime.datetime.strptime(timestamp, GMT_FORMAT) + datetime.timedelta(hours=8)
        now = local_time.strftime("%Y-%m-%d %H:%M:%S")
        return now

    def downloadLatestRelease(self, moduleJson, downloadPath):
        try:
            print(downloadPath)
            ghRepo = self.github.get_repo(moduleJson["repo"])
        except:
            print("无法获取: ", moduleJson["repo"])
            return

        ghLatestTag = ghRepo.get_tags()[0]
        # print( "last tag: " + ghLatestTag.name) # v1.0
        # print( "time: " + ghLatestTag.last_modified) # Fri, 23 Oct 2020 04:21:50 GMT
        # print( "raw: " + ghLatestTag.raw_data)
        # commit = ghLatestTag.commit # Commit(sha="7e700a25a6cb378d5c04d7cb3d616c14546d1c6b")
        # timestamp =  commit.stats.last_modified # # Fri, 23 Oct 2020 04:21:50 GMT
        now = self.formatGMTime(timestamp)
        # print("last modified: " + now)
        
        info = {"tag":ghLatestTag.name,"last_modified":now,"url": ghLatestTag.zipball_url}
        print(info)
        
        releases = ghRepo.get_releases()
        if releases.totalCount == 0:
            print("无可用版本: ", moduleJson["repo"])
            return
        ghLatestRelease = releases[0]

        downloadedFiles = []

        ghBody = ghLatestRelease.body

        for pattern in moduleJson["assetRegex"]:
            matched_asset = None
            for asset in ghLatestRelease.get_assets():
                if re.search(pattern, asset.name):
                    matched_asset = asset
                    url = asset.browser_download_url
                    updated_at = matched_asset.updated_at
                    updated_at_utc8 = updated_at + datetime.timedelta(hours=8)
                    updated_at_utc8_str = updated_at_utc8.strftime("%Y-%m-%d %H:%M:%S")
                    version = None
                    pattern = re.compile(rf'{matched_asset.name.split(".")[0]}\|(.*?)\|')
                    match = re.search(pattern, ghBody)
                    if match:
                        version = match.group(1)
                    else:
                        version = ghLatestTag.name
                    # print(version)
                    info = {"tag":version,"last_modified":updated_at_utc8_str,"url": url}
                    print(info)
                    break
            if matched_asset is None:
                print("未找到文件: ", pattern)
                return

            downloadFilePath = Path.joinpath(downloadPath, matched_asset.name)
            # print("downloadFilePath: ", downloadFilePath)
            urllib.request.urlretrieve(matched_asset.browser_download_url, downloadFilePath)
            downloadedFiles.append(downloadFilePath)
        
        # return downloadedFiles
        return info
