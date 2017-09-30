import csv

with open('edges.txt', 'r') as infile:
	list = infile.read().split("),")

newlist = [(item.strip()[1:-1].split(",")[0], item.strip()[1:-1].split(",")[1]) for item in list]
print(newlist[0][0])
with open('edges.csv','w') as out:
    csv_out=csv.writer(out)
    for item in newlist:
        csv_out.writerow([item[0].strip()[1:-1], item[1].strip()[1:]])
