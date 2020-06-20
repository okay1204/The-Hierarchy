import sqlite3
from sqlite3 import Error


conn = sqlite3.connect('hierarchy.db')
c = conn.cursor()
c.execute('SELECT id, total FROM members')
hierarchy = c.fetchall()
conn.close()
sorted_list = sorted(hierarchy, key=lambda k: k[1], reverse=True)
print(sorted_list)
listids = []
userid = int(input('Enter id: '))
find = int(input('Enter range: '))
for x in sorted_list:
    listids.append(x[0])
cindex = listids.index(userid)
result = []
iszero = False
haszero = False
if sorted_list[cindex][1] == 0: 
    sorted_list = list(filter(lambda x: x[1] != 0 or x[0] == userid, sorted_list))
    listids = []
    for x in sorted_list:
        listids.append(x[0])
    cindex = listids.index(userid)
if sorted_list[cindex][1] == 0: 
    iszero = True
elif any(x[1] == 0 for x in sorted_list[cindex-find:cindex+find+1]):
    haszero = True
negextra = 0
posextra = 0
for x in range(-1*find, find+1):
    index = cindex + x
    if iszero and index > cindex:
        continue
    if haszero and sorted_list[index][1] == 0:
        negextra += 1
        continue
    if index < 0:
        posextra += 1
        continue
    result.append(sorted_list[index])
for x in range(negextra):
    index = cindex - find - negextra
    result.insert(0, sorted_list[index])
for x in range(posextra):
    index = cindex + find + posextra
    result.append(sorted_list[index])
listids = []
for x in result:
    listids.append(x[0])
rindex = listids.index(userid)
if len(sorted_list[0:cindex]) < find:
    result.insert(0, ('Steal Divider', 'Steal Divider'))
else:
    num = rindex-3
    if num < 0:
        pass
    else:
        print(rindex)
        result.insert(num, ('Steal Divider', 'Steal Divider'))


if sorted_list[cindex][1] == 0:
    result.append(('Steal Divider', 'Steal Divider'))

print(result)