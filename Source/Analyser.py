from pymongo import MongoClient
import operator
from decimal import *
import math

def print_stats(wins, games):
    total = games.count()
    nbWins = wins.count()
    print "Total wins :", nbWins

    pcent = Decimal(nbWins) / Decimal(total) * 100
    print "Win percentage : " + str(round(pcent,2)) + "%"


    ## Total games
    # games = db.catane.find()

    total_bois = {}
    total_ble = {}
    total_argile = {}
    total_mineral = {}
    total_laine = {}
    total_configs = {}

    for w in games:
        if w['bois'] not in total_bois:
            total_bois[w['bois']] = 0
        total_bois[w['bois']] += 1

        if w['ble'] not in total_ble:
            total_ble[w['ble']] = 0
        total_ble[w['ble']] += 1

        if w['argile'] not in total_argile:
            total_argile[w['argile']] = 0
        total_argile[w['argile']] += 1

        if w['mineral'] not in total_mineral:
            total_mineral[w['mineral']] = 0
        total_mineral[w['mineral']] += 1

        if w['laine'] not in total_laine:
            total_laine[w['laine']] = 0
        total_laine[w['laine']] += 1

        config = (w['ble'], w['argile'], w['bois'], w['mineral'], w['laine'], )
        if config not in total_configs:
            total_configs[config] = 0
        total_configs[config] += 1


    ## Wins
    # win = db.catane.find({'score': {'$in': ["10","11","12","13","14","15"]}})

    bois = {}
    ble = {}
    argile = {}
    mineral = {}
    laine = {}

    configs = {}

    for w in wins:
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

        config = (w['ble'], w['argile'], w['bois'], w['mineral'], w['laine'], )
        if config not in configs:
            configs[config] = 0
        configs[config] += 1



    win_ratio_bois = {}
    win_ratio_ble = {}
    win_ratio_argile = {}
    win_ratio_mineral = {}
    win_ratio_laine = {}
    win_ratio_configs = {}

    for key, val in total_bois.iteritems():
        win_ratio_bois[key] = Decimal(bois[key]) / Decimal(total_bois[key])

    for key, val in total_ble.iteritems():
        win_ratio_ble[key] = Decimal(ble[key]) / Decimal(total_ble[key])

    for key, val in total_argile.iteritems():
        win_ratio_argile[key] = Decimal(argile[key]) / Decimal(total_argile[key])

    for key, val in total_mineral.iteritems():
        win_ratio_mineral[key] = Decimal(mineral[key]) / Decimal(total_mineral[key])

    for key, val in total_laine.iteritems():
        win_ratio_laine[key] = Decimal(laine[key]) / Decimal(total_laine[key])

    for key, val in total_configs.iteritems():
        try:
            win_ratio_configs[key] = Decimal(configs[key]) / Decimal(total_configs[key])
        except Exception:
            print 'oups'

    sorted_bois = sorted(bois.items(), key=operator.itemgetter(1), reverse=True)
    sorted_ble = sorted(ble.items(), key=operator.itemgetter(1), reverse=True)
    sorted_argile = sorted(argile.items(), key=operator.itemgetter(1), reverse=True)
    sorted_mineral = sorted(mineral.items(), key=operator.itemgetter(1), reverse=True)
    sorted_laine = sorted(laine.items(), key=operator.itemgetter(1), reverse=True)
    sorted_configs = sorted(configs.items(), key=operator.itemgetter(1), reverse=True)

    sorted_win_ratio_bois = sorted(win_ratio_bois.items(), key=operator.itemgetter(1), reverse=True)
    sorted_win_ratio_ble = sorted(win_ratio_ble.items(), key=operator.itemgetter(1), reverse=True)
    sorted_win_ratio_argile = sorted(win_ratio_argile.items(), key=operator.itemgetter(1), reverse=True)
    sorted_win_ratio_mineral = sorted(win_ratio_mineral.items(), key=operator.itemgetter(1), reverse=True)
    sorted_win_ratio_laine = sorted(win_ratio_laine.items(), key=operator.itemgetter(1), reverse=True)
    sorted_win_ratio_configs = sorted(win_ratio_configs.items(), key=operator.itemgetter(1), reverse=True)

    print "Wins"
    print 'bois',sorted_bois
    print 'ble',sorted_ble
    print 'argile',sorted_argile
    print 'mineral',sorted_mineral
    print 'laine',sorted_laine
    print 'configs',sorted_configs


    print "Win ratios"
    print 'bois',sorted_win_ratio_bois
    print 'ble',sorted_win_ratio_ble
    print 'argile',sorted_win_ratio_argile
    print 'mineral',sorted_win_ratio_mineral
    print 'laine',sorted_win_ratio_laine
    print 'configs',sorted_win_ratio_configs

    for cfg in sorted_win_ratio_configs:
        print "Config " + str(cfg[0]) + " has a win ratio of " + str(round(cfg[1] * 100, 2)) + " (" + str(configs[cfg[0]]) + '/' + str(total_configs[cfg[0]]) + ')'

    # f = file('top100.txt', 'w')
    # for i in range(100):
    #     f.write(str(sorted_win_ratio_configs[i][0]) + "\n")
    # f.close()

# Open DB connection
connection = MongoClient('nebula.step.polymtl.ca')
connection.alexrose.authenticate('alexrose', 'allo')
db = connection.alexrose

# Print stats - catane
# total = db.catane.count()
# print "Total entries :", total
#
# wins = db.catane.find({'score': {'$in': ["10","11","12","13","14","15"]}})
# games = db.catane.find()
#
# print_stats(wins, games)

# Print stats - catane2
# total = db.catane2.count()
# print "Total entries :", total
#
# wins = db.catane2.find({'score': {'$in': ["10","11","12","13","14","15"]}})
# games = db.catane2.find()
#
# print_stats(wins, games)

# Print stats - catane3
total = db.catane3.count()
print "Total entries :", total

wins = db.catane3.find({'score': {'$in': ["10","11","12","13","14","15"]}})
games = db.catane3.find()

print_stats(wins, games)