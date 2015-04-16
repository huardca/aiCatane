from pymongo import MongoClient
import operator

connection = MongoClient('nebula.step.polymtl.ca')
connection.alexrose.authenticate('alexrose', 'allo')
db = connection.alexrose

win = db.catane.find({'score': '10'})

bois = {}
ble = {}
argile = {}
mineral = {}
laine = {}

for w in win:
    if w['bois'] not in bois:
        bois[w['bois']] = 0
    bois[w['bois']] += 1

    if w['ble'] not in ble:
        ble[w['ble']] = 0
    ble[w['ble']] += 1

    if w['argile'] not in argile:
        argile[w['argile']] = 0
    argile[w['argile']] += 1

    if w['mineral'] not in mineral:
        mineral[w['mineral']] = 0
    mineral[w['mineral']] += 1

    if w['laine'] not in laine:
        laine[w['laine']] = 0
    laine[w['laine']] += 1

bois = sorted(bois.items(), key=operator.itemgetter(1), reverse=True)
ble = sorted(ble.items(), key=operator.itemgetter(1), reverse=True)
argile = sorted(argile.items(), key=operator.itemgetter(1), reverse=True)
mineral = sorted(mineral.items(), key=operator.itemgetter(1), reverse=True)
laine = sorted(laine.items(), key=operator.itemgetter(1), reverse=True)

print 'bois',bois
print 'ble',ble
print 'argile',argile
print 'mineral',mineral
print 'laine',laine