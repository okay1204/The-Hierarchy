import sqlite3
from sqlite3 import Error

def around(userid, find):
    conn = sqlite3.connect('hierarchy.db')
    c = conn.cursor()
    c.execute('SELECT id, total FROM members')
    hierarchy = c.fetchall()
    conn.close()
    sorted_list = sorted(hierarchy, key=lambda k: k[1], reverse=True)
    listids = []
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
        print('haszero')
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
    return result

print(around(int(input("id: ")), int(input("range: "))))