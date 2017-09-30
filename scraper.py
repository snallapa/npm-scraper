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
	if package.get("dist-tags", None) == None :
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

dependenciesToSearch = ["mongoose"]
dependenciesSearched = []
dependenciesEdges = []
while len(dependenciesToSearch) != 0:
	currentDependencyName = dependenciesToSearch[0]

	if currentDependencyName in dependenciesSearched:
		dependenciesToSearch = dependenciesToSearch[1:]
		continue
	print(currentDependencyName)
	currentDependency = getPackageData(currentDependencyName)
	if currentDependency == None:
		dependenciesSearched.append(currentDependencyName)
		dependenciesToSearch = dependenciesToSearch[1:]
		continue

	dependenciesToSearch = dependenciesToSearch + currentDependency.dependencies
	dependenciesEdges.extend([(currentDependencyName, dependency) for dependency in currentDependency.dependencies])
	dependenciesSearched.append(currentDependencyName)
	dependenciesToSearch = dependenciesToSearch[1:]
	
f = open('nodes.txt', 'w')
f.write(json.dumps(dependenciesMap))
f.close()
f2 = open('edges.txt', 'w')
f2.write(json.dumps(str(dependenciesEdges))[2:-2])
f2.close()
	