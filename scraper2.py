import urllib.request, urllib.error, json
from time import sleep

def getPackageData(name):
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
	dependencies = getPackageData(currentDependencyName)
	dependenciesToSearch = dependenciesToSearch + dependencies
	dependenciesEdges.extend([(dependency, currentDependencyName) for dependency in dependencies])
	dependenciesSearched.append(currentDependencyName)
	dependenciesToSearch = dependenciesToSearch[1:]
#f = open('nodes.txt', 'w')
#f.write(json.dumps(dependenciesMap))
#f.close()
f2 = open('edges2.txt', 'w')
f2.write(json.dumps(str(dependenciesEdges))[2:-2])
f2.close()
	