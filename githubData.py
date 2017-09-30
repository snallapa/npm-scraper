import urllib.request, urllib.error, json
from functools import reduce 

def find_between(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def getOwnerAndRepo(repoUrl):
    query = find_between(repoUrl.replace(":","/") + ".git", "github.com/", ".git")
    if query == "":
        return None
    return query.split("/")

def getCommitsForPages(link):
    last = link.split(",")[1]
    lastPage = int(find_between(last, "page=", ">"))
    commitCount = (lastPage - 1) * 30
    try:
        with urllib.request.urlopen(find_between(last,"<", ">")) as url:
            lastCommits = json.loads(url.read().decode())
            return commitCount + len(lastCommits)
    except urllib.error.HTTPError:
        print("could not find package " + name)
        return None
    except urllib.error.URLError:
        sleep(1)
        return getPackageData(name)

def getCommits(owner, repo, author=""):
    requestUrl = ""
    if author == "":
        requestUrl = "https://api.github.com/repos/{}/{}/commits".format(owner, repo)
    else:
        requestUrl = "https://api.github.com/repos/{}/{}/commits?author={}".format(owner, repo, author)
    try:
        with urllib.request.urlopen(requestUrl) as url:
            commits = json.loads(url.read().decode())
            
            linkHeader = url.info().get("Link", None)
            if linkHeader == None:
                return len(commits)
            else:
                return getCommitsForPages(linkHeader)
    except urllib.error.HTTPError:
        print("404ed url: {}".format(requestUrl))
        return None
    except urllib.error.URLError:
        sleep(1)
        return getPackageData(name)

#print(getCommits("Automattic", "mongoose", "rauchg@gmail.com"))
counter1 = 0
counter2 = 0
weirdPackages = []
with open('nodes.txt') as nodesFile:    
    nodes = json.load(nodesFile)
packages = list(nodes.keys())
for package in packages:
    repo = nodes[package].get("repo", None)
    if repo == None or repo == "":
        counter1 = counter1 + 1
        continue
    url = repo
    if type(repo) is dict:
        url = repo.get("url", "")
    if type(repo) is list:
        url = repo[0].get("url", "")
    ownerAndRepo = getOwnerAndRepo(url)
    if url == '':
        counter1 = counter1 + 1
        continue
    if ownerAndRepo == None:
        counter2 = counter2 + 1
        weirdPackages.append(url)
        continue
    

print("{} number of packages did not have a repo".format(counter1))
print("{} number of packages had a different repo".format(counter2))
bitbucketCount = reduce((lambda count, i: count + ("bitbucket" in i)), weirdPackages, 0)
gitlab = reduce((lambda count, i: count + ("gitlab" in i)), weirdPackages, 0)
github = reduce((lambda count, i: count + ("github" in i)), weirdPackages, 0)
print("{} number of packages on bitbucket".format(bitbucketCount))
print("{} number of packages on gitlab".format(gitlab))
print("{} number of packages on github but malformed".format(github))