import os


for filename in os.listdir("RawSheets"):
    with open('RawSheets/' + filename) as f:
        data = f.read()
        data=data.replace('\\"','\"')
        data = data.replace('"events":"', '"events":')
        data = data.replace(']"', ']')
        f = open('GameSheets/' + filename, "w")
        f.write(data)
        f.close()

for filename in os.listdir("RawSheets"):
    os.remove('RawSheets/' + filename)