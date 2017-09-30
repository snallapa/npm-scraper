import urllib.request, urllib.error, json
from time import sleep

class Package(json.JSONEncoder):
	def __init__(self, dependencies, maintainers, repo, author):
		self.dependencies = dependencies
		self.maintainers = maintainers
		self.author = author
		self.repo = repo

	def __str__(self):
		return str(self.dependencies) + "\n" + str(self.maintainers) + "\n" + str(self.repo) + "\n" + author

def getPackage(package):
	if package.get("dist-tags", None) == None or package["dist-tags"].get("latest", None) == None:
		return None
	latestVersionString = package["dist-tags"]["latest"]
	latestVersion = package["versions"][latestVersionString]
	dependencies = set([key for key in latestVersion.get("dependencies", [])] + [key for key in latestVersion.get("devDependencies",[])]);
	repo = latestVersion.get("repository", None)
	maintainers = latestVersion.get("maintainers", [])
	author = latestVersion.get("author", None)
	return Package(list(dependencies), maintainers, repo, author)


dependenciesMap = {}

def getPackageData(name):
	savedDependency = dependenciesMap.get(name, None)
	if savedDependency:
		return savedDependency
	try:
		with urllib.request.urlopen("https://registry.npmjs.org/" + name.replace("/", "%2f")) as url:
			package = json.loads(url.read().decode())
			packageObj = getPackage(package)
			if packageObj != None:
				dependenciesMap[name] = packageObj.__dict__
			return packageObj
	except urllib.error.HTTPError:
		print("could not find package " + name)
		return None
	except urllib.error.URLError:
		sleep(1)
		return getPackageData(name)


def getPackageDependents(name):
	try:
		with urllib.request.urlopen("https://skimdb.npmjs.com/registry/_design/app/_view/dependentVersions?startkey=%5B%22" + name + "%22%5D&endkey=%5B%22" + name + "%22%2C%7B%7D%5D&reduce=false") as url:
			package = json.loads(url.read().decode())
			dependencies = list(map((lambda item: item["id"]),package.get("rows", [])))
			return dependencies
	except urllib.error.HTTPError:
		print("could not find package " + name)
		return []
	except urllib.error.URLError:
		sleep(1)
		print("timed out retrying")
		return getPackageData(name)

dependenciesSearched = {}
dependenciesToSearch = ["mongoose"]

dependenciesEdges = []
counter = 0
while len(dependenciesToSearch) != 0:
	if counter == 15:
		print("Packages to search: " + str(len(dependenciesToSearch)))
		counter = 0
	currentDependencyName = dependenciesToSearch[0]
	if dependenciesSearched.get(currentDependencyName, False):
		dependenciesToSearch = dependenciesToSearch[1:]
		continue
	print(currentDependencyName)
	#find the packages dependencies
	currentDependency = getPackageData(currentDependencyName)
	if currentDependency == None:
		dependenciesSearched[currentDependencyName] = True
		dependenciesToSearch = dependenciesToSearch[1:]
		continue

	#update the dependencies to search and the edges
	dependenciesToSearch = dependenciesToSearch + list(filter((lambda x: not dependenciesSearched.get(x, False)), currentDependency.dependencies))
	dependenciesEdges = dependenciesEdges + [(currentDependencyName, dependency) for dependency in currentDependency.dependencies]

	#find the packages that are dependent on the current one
	currentDependents = getPackageDependents(currentDependencyName)
	if currentDependents == None:
		dependenciesSearched[currentDependencyName] = True
		dependenciesToSearch = dependenciesToSearch[1:]
		continue
	if type(currentDependents) is dict:
		print("wtf how not a dict error " + str(currentDependencyName))
		dependenciesSearched[currentDependencyName] = True
		dependenciesToSearch = dependenciesToSearch[1:]
		continue
	#update the dependencies to search and the edges
	dependenciesToSearch = dependenciesToSearch + list(filter((lambda x: not dependenciesSearched.get(x, False)), currentDependents))
	dependenciesEdges = dependenciesEdges + [(currentDependent, currentDependencyName) for currentDependent in currentDependents]

	#add the current item to the searched list
	dependenciesSearched[currentDependencyName] = True
	dependenciesToSearch = dependenciesToSearch[1:]
	counter = counter + 1

f = open('nodes.txt', 'w')
f.write(json.dumps(dependenciesMap))
f.close()
f2 = open('edges.txt', 'w')
f2.write(json.dumps(str(list(dependenciesEdges)))[2:-2])
f2.close()
