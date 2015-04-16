#!/usr/bin/python
#-*- coding: latin-1 -*-


from Joueur import *
from Mappe import *

class Strategy:
    ROADS = 0
    CITIES = 1

class State:
    EXPAND = 0
    MATURE = 1
    END = 2
    FINISH = 3

class Commodity:
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    CARD = 3

class Endgame:
    LONGEST_ROAD = 0
    LARGEST_ARMY = 1
    SETTLEMENT = 2
    CITY = 3

class HumanAction:
    def __init__(self, action, data, score):
        self.action = action
        self.data = data
        self.score = score

    def output(self):
        return self.data

################## Joueur Intelligent
class JoueurHumain(Joueur):


    def __init__(self,id):
        super(JoueurHumain,self).__init__(id)

        print "HUMAIN: " + str(id)


        self.premiereColonie = {}
        self.premiereIntersectionRoute = {}
        self.deuxiemeColonie = {}
        self.deuxiemeIntersectionRoute = {}

        self.strategy = Strategy.ROADS
        self.state = State.EXPAND

        self.incomeStats = [0.0, 0.0, 0.0, 0.0, 0.0]
        # self.resourceValues = [1, 1.2, 1.1, 0.9, 0.8] #BLÉ, ARGILE, BOIS, MINÉRAL, LAINE

        self.estHumain = True

    def setValues(self, values):
        self.resourceValues = values

    def premierTour(self,mappe):

        self.premiereColonie = self.trouverMeilleureIntersectionColonie(mappe)
        self.premiereIntersectionRoute = self.trouverMeilleureIntersectionRoute(self.premiereColonie,mappe)[0]

        if(self.premiereIntersectionRoute is None):
            self.premiereIntersectionRoute = self.getLessBadRoad(self.premiereColonie, mappe)

        self.ajusterIncomeStats(mappe, self.premiereColonie)

        return (self.premiereColonie._id,self.premiereIntersectionRoute._id)


    def deuxiemeTour(self,mappe):

        self.deuxiemeColonie = self.trouverMeilleureIntersectionColonie(mappe)
        self.deuxiemeIntersectionRoute = self.trouverMeilleureIntersectionRoute(self.deuxiemeColonie,mappe)[0]

        if(self.deuxiemeIntersectionRoute is None):
            self.deuxiemeIntersectionRoute = self.getLessBadRoad(self.deuxiemeColonie, mappe)

        self.ajusterIncomeStats(mappe, self.deuxiemeColonie)

        if self.incomeStats[Ressource.MINERAL] + self.incomeStats[Ressource.BLE] > \
                        self.incomeStats[Ressource.ARGILE] + self.incomeStats[Ressource.BOIS]:
            self.strategy = Strategy.CITIES

        return (self.deuxiemeColonie._id,self.deuxiemeIntersectionRoute._id)


    def choisirAction(self,mappe,infoJoueurs,paquetCartesVide):

        self.state = self.chooseState(mappe)

        if self.peutJouerCarteChevalier():
            return (Action.JOUER_CARTE_CHEVALIER, [])

        if(self.state == State.EXPAND):
            action = self.expand(mappe)
            if action is not None:
                return action
            print("TRY CITY")
            action = self.tryBuildBestCity(mappe)
            if action is not None:
                return action

            action = self.roadOrCard(mappe, infoJoueurs)
            if action is not None:
                return action

            if self.peutJouerCarteChevalier():
                return (Action.JOUER_CARTE_CHEVALIER, self.jouerVoleurs(mappe, infoJoueurs))

        elif self.state == State.MATURE:
            print("TRY CITY")
            action = self.tryBuildBestCity(mappe)
            if action is not None:
                return action
            action = self.expand(mappe)
            if action is not None:
                return action
            action = self.roadOrCard(mappe, infoJoueurs)
            if action is not None:
                return action
        elif self.state == State.END:
            print("TRY CITY")
            action = self.tryBuildBestCity(mappe)
            if action is not None:
                return action
            action = self.expand(mappe)
            if action is not None:
                return action
            action = self.roadOrCard(mappe, infoJoueurs)
            if action is not None:
                return action


        self.gererExtra()

        print 'TERMINER'
        return Action.TERMINER

    def gererExtra(self):
        pass

    def roadOrCard(self, mappe, infoJoueurs):
        if self.favorRoad(mappe, infoJoueurs):
            if self.shouldBuildRoad(mappe):
                print("BUILD LONGEST ROAD")
                action = self.tryBuildBestRoad(mappe, True)
                if action is not None:
                    return action
            if self.shouldBuyCard(mappe, infoJoueurs):
                print("TRY CARTE")
                action = self.tryBuildCommodity(Action.ACHETER_CARTE, [], False)
                if action is not None:
                   return action
        else:
            if self.shouldBuyCard(mappe, infoJoueurs):
                print("TRY CARTE")
                action = self.tryBuildCommodity(Action.ACHETER_CARTE, [], False)
                if action is not None:
                   return action
            if self.shouldBuildRoad(mappe):
                print("BUILD LONGEST ROAD")
                action = self.tryBuildBestRoad(mappe, True)
                if action is not None:
                    return action
        return None

    def tryBuildBestCity(self, mappe):

        bestCity = None
        bestScore = 0

        for i in [mappe.obtenirIntersection(x) for x in mappe.obtenirNumerosIntersectionsJoueur(self._id)]:
            if i._occupation == Occupation.COLONIE:
                score = self.calculerScoreIntersectionColonie(i,mappe)
                print(score)

                if score > bestScore:
                    bestScore = score
                    bestCity = i

        if bestCity is not None:
            return self.tryBuildCommodity(Action.AJOUTER_VILLE,[bestCity._id], True)

        return None

    def tryBuildBestRoad(self, mappe, anyRoad):

        bestRoad = None
        bestRoadOrigin = None
        bestRoadScore = 0

        allRoads = []

        for i in mappe.obtenirToutesLesIntersections():
            if mappe._accesRoute(i._id,self._id):
                potentialRoad = self.trouverMeilleureIntersectionRoute(i, mappe)

                for v in i.obtenirVoisins():
                    if mappe.intersectionPossedeRoute(i._id, v._id):
                        allRoads.append((i, v))

                if potentialRoad[1] > bestRoadScore:
                    bestRoad = potentialRoad[0]
                    bestRoadScore = potentialRoad[1]
                    bestRoadOrigin = i

        if bestRoad is not None:
            return self.tryBuildCommodity(Action.AJOUTER_ROUTE,[bestRoadOrigin._id, bestRoad._id], True)

        if anyRoad:

            intersections = [i for i in range(1,55) if mappe._accesRoute(i,self._id)]

            max = 0
            longestStart = []
            for i in intersections:
                l = mappe._plusLong(i,[],self._id)
                # S'il s'ajout du plus long jusqu'à maintenant, on mémorise cette valeur
                if l > max:
                    max = l
                    longestStart = [mappe.obtenirIntersection(i)]
                elif l == max:
                    longestStart.append(mappe.obtenirIntersection(i))

            bestRoads = []
            for i in longestStart:
                for v in i.obtenirVoisins():
                    if mappe.intersectionPossedeRoute(i._id, v._id):
                        bestRoads.append((i, v))

            if len(bestRoads) > 0:
                randomRoute = random.choice(bestRoads)
                return self.tryBuildCommodity(Action.AJOUTER_ROUTE,[randomRoute[0]._id,randomRoute[1]._id], True)

            if len(allRoads) > 0:
                randomRoute = random.choice(allRoads)
                return self.tryBuildCommodity(Action.AJOUTER_ROUTE,[randomRoute[0]._id,randomRoute[1]._id], True)

        return None

    def tryBuildCommodity(self, action, data, trade):

        print("try build " + str(action))
        necessaryResources = []

        if(action == Action.AJOUTER_ROUTE):
            necessaryResources = [0,1,1,0,0]
        if(action == Action.AJOUTER_COLONIE):
            necessaryResources = [1,1,1,0,1]
        if(action == Action.ACHETER_CARTE):
            necessaryResources = [1,0,0,1,1]
        if(action == Action.AJOUTER_VILLE):
            necessaryResources = [2,0,0,3,0]

        ressourceDiff = [self._ressources[x] - y for x, y in zip(self._ressources, necessaryResources)]

        if not any(t < 0 for t in ressourceDiff):
            if data is None:
                return action
            else:
                return (action,data)

        if(not trade):
            return None

        priorityList = self.priorityList()

        firstTrade = None

        for r in priorityList:
            if(ressourceDiff[r] >= 0):
                continue

            for r2 in priorityList[::-1]:
                nbTrade = 0
                if r2 in self._peutEchanger and ressourceDiff[r2] >= 2:
                    nbTrade = 2
                elif self._possedePortGenerique and ressourceDiff[r2] >= 3:
                    nbTrade = 3
                elif ressourceDiff >= 4:
                    nbTrade = 4

                if nbTrade > 0 and ressourceDiff[r2] >= nbTrade:
                    if not any(t < 0 for t in ressourceDiff):
                        break

                    while(ressourceDiff[r] < 0 and ressourceDiff[r2] >= nbTrade):
                        if firstTrade is None:
                            firstTrade = (Action.ECHANGER_RESSOURCES,[nbTrade, r2, r])
                        ressourceDiff[r] += 1
                        ressourceDiff[r2] -= nbTrade

        if not any(t < 0 for t in ressourceDiff):
            print("ON ECHANGE: " + str(firstTrade))
            return firstTrade

        print("FAIL " + str(action))
        return None

    def priorityList(self):
        return [Ressource.ARGILE, Ressource.BOIS, Ressource.BLE, Ressource.LAINE, Ressource.MINERAL] \
            if self.state == State.EXPAND else [Ressource.MINERAL, Ressource.BLE, Ressource.ARGILE, Ressource.BOIS, Ressource.LAINE]

    def getBestNeighbor(self, bestIntersection, mappe):

        maxScore = 0
        meilleureIntersection = None
        origineIntersection = None

        for i in mappe.obtenirToutesLesIntersections():
            if mappe._accesRoute(i._id,self._id):
                for j in i.obtenirVoisins():
                    if mappe.peutConstruireOccupation(j._id, self._id): #si on peut poser une colonie sur l'intersection
                        if not j.occupe():
                            score = self.calculerScoreIntersectionColonie(j, mappe)

                            if(score > maxScore):
                                maxScore = score
                                meilleureIntersection = j
                                origineIntersection = i

        if maxScore > 1.5 * self.calculerScoreIntersectionColonie(bestIntersection, mappe):
            return (origineIntersection,meilleureIntersection)

        return (None, None)

    def getLessBadRoad(self, intersection, mappe):
        #TODO: Mieux faire ceci
        return intersection.obtenirVoisins()[0]

    def getBestColonySpot(self, mappe):
        maxScore = 0
        meilleureIntersection = None

        for i in mappe.obtenirToutesLesIntersections(): #pour toutes les intersections
            if mappe.peutConstruireOccupation(i._id, self._id): #si on peut poser une colonie sur l'intersection
                if not i.occupe():
                    score = self.calculerScoreIntersectionColonie(i, mappe)

                    if(score > maxScore):
                        maxScore = score
                        meilleureIntersection = i

        return meilleureIntersection

    def chooseState(self, mappe):

        if(self.state == State.EXPAND):
            if len(mappe.obtenirNumerosIntersectionsJoueur(self._id)) >= 4:
                self.state = State.MATURE
        elif(self.state == State.MATURE):
            if self._pointsVictoire >= 7:
                self.state = State.END
        elif(self.state == State.END):
            pass
            # TODO: THIS
            #if self._pointsVictoire >= 9:
            #    self.state = State.FINISH

        return self.state


    def ajusterIncomeStats(self, mappe, intersection):
        if intersection is None:
            return

        i = mappe.obtenirIntersection(intersection.id())

        for t in i.obtenirTerritoiresVoisins():
            if t.ressource() is not None:
                self.incomeStats[t.ressource()] += float(self.obtenirValeurProductionChiffre(t._valeur)) / 36.0


    def trouverMeilleureIntersectionColonie(self,mappe):

        maxScore = 0
        meilleureIntersection = None

        for i in mappe.obtenirToutesLesIntersections(): #pour toutes les intersections
            if mappe.peutConstruireOccupationInitial(i._id): #si on peut poser une colonie sur l'intersection
                if not i.occupe():
                    score = self.calculerScoreIntersectionColonie(i, mappe)

                    if(score > maxScore):
                        maxScore = score
                        meilleureIntersection = i

        print "COLONIE"
        print meilleureIntersection._id

        return meilleureIntersection

    def calculerScoreIntersectionColonie(self, intersection, mappe):

        score = 0
        GEN_MULTIPLIER = 1.2
        SPEC_MULTIPLIER = 1.5

        genericMultiplier = GEN_MULTIPLIER if isinstance(intersection,PortGenerique) or self._possedePortGenerique else 1
        newIncome = list(self.incomeStats)

        for t in intersection.obtenirTerritoiresVoisins(): #pour tous les territoires de l'intersection
            if t.ressource() is not None:
                newIncome[t.ressource()] += float(self.obtenirValeurProductionChiffre(t._valeur)) / 36.0

        if isinstance(intersection,PortSpecialise):
            if not self.peutEchangerPortSpecialise(intersection.ressource()):
                newIncome[intersection.ressource()] *= SPEC_MULTIPLIER

        for r in self._peutEchanger:
            newIncome[r] *= SPEC_MULTIPLIER

        for idx, r in enumerate(newIncome):
            score += r * genericMultiplier - self.incomeStats[idx] * (GEN_MULTIPLIER if self._possedePortGenerique else 1)

        return score

    def trouverMeilleureIntersectionRoute(self,intersection,mappe):

        bestRoad = None
        maxRoadScore = 0

        for i in intersection.obtenirVoisins():
            if not mappe.intersectionPossedeRoute(intersection._id, i._id):
                continue
            scoreRoad = 0
            for j in i.obtenirVoisins():
                if not mappe.intersectionPossedeRoute(i._id, j._id):
                    continue
                if not j.occupe() and j != intersection and mappe.peutConstruireOccupationInitial(j._id):
                    scoreRoad += self.calculerScoreIntersectionColonie(j, mappe)
            if scoreRoad > maxRoadScore:
                bestRoad = i
                maxRoadScore = scoreRoad

        return (bestRoad,maxRoadScore)


    def obtenirValeurProductionChiffre(self,chiffre):

        if chiffre == 2 or chiffre == 12:
            return 1
        elif chiffre == 3 or chiffre == 11:
            return 2
        elif chiffre == 4 or chiffre == 10:
            return 3
        elif chiffre == 5 or chiffre == 9:
            return 4
        elif chiffre == 0:
            return 0
        else:
            return 5


    def deciderJouerCarteChevalier(self,mappe,infoJoueurs):

        voleurSurMaRegion = False
        ennemiBonneZone = False

        for i in mappe.obtenirTerritoireContenantVoleurs().obtenirVoisins():
            if i.obtenirOccupant() == self._id:
                voleurSurMaRegion = True
                break

        joueurAVoler = False
        territoireAVoler = False

        for t in mappe.obtenirTousLesTerritoires():

            if t._valeur == 6 or t._valeur == 8:

                for i in t.obtenirVoisins():
                    if i.obtenirOccupant() != self._id and i.obtenirOccupant() != None:
                        ennemiBonneZone = True
                        joueurAVoler = i.obtenirOccupant()
                        territoireAVoler = t



            if joueurAVoler != False:
                break;

        if ennemiBonneZone and voleurSurMaRegion:
            return [territoireAVoler._id, joueurAVoler]

        else:
            return False

    def jouerVoleurs(self,mappe,infoJoueurs):

        return (0,0)

        max = 0
        maxPlayer = 0

        for i in range(len(infoJoueurs)):
            if infoJoueurs[i] == self.id():
                continue

            if infoJoueurs[i][1] == 0:
                continue

            if infoJoueurs[i][0] > max:
                max = infoJoueurs[i][0]
                maxPlayer = i

        intersections = mappe.obtenirNumerosIntersectionsJoueur(maxPlayer)

        territoires = []

        for intersection in intersections:
            for ter in mappe.obtenirIntersection(intersection).obtenirTerritoiresVoisins():
                if ter not in territoires:
                    territoires.append(ter)

        voisins = {}
        for ter in territoires:
            voisins[ter.id()] = 0

            for int in ter.obtenirVoisins():
                if int.id() in intersections:
                    voisins[ter.id()] += 1

        if mappe.obtenirTerritoireContenantVoleurs().id() in voisins:
            del voisins[mappe.obtenirTerritoireContenantVoleurs().id()]
        max = -1
        maxInt = -1
        for key, value in voisins.iteritems():
            if value > max:
                max = value
                maxInt = key

        return (maxInt,maxPlayer)  # Retourne une paire non valide


    def possibleAcheterCarte(self):

        if self.quantiteRessources(Ressource.BLE) >= 1 and self.quantiteRessources(Ressource.LAINE) >= 1 and self.quantiteRessources(Ressource.MINERAL) >= 1:
            return True

        else:
            return False

    # Se fait voler une carte
    # Deux choix, carte chevalier, voleur
    def pigerRessourceAleatoirement(self):
        super(JoueurHumain, self).pigerRessourceAleatoirement()

    def expand(self, mappe):
        spot = self.getBestColonySpot(mappe)
        if spot is not None:
            print ("SPOT: " + str(spot._id))
            bestNeighbor = self.getBestNeighbor(spot, mappe)
            if bestNeighbor[1] is not None:
                print("BEST NEIGHBOR: " + str(bestNeighbor[1]._id))
                action = self.tryBuildCommodity(Action.AJOUTER_ROUTE, [bestNeighbor[0]._id, bestNeighbor[1]._id], True)
                if action is not None:
                    return action
            else:
                print("NO BEST NEIGHBOR")
                action = self.tryBuildCommodity(Action.AJOUTER_COLONIE, [spot._id], True)
                if action is not None:
                    return action
        else:
            print("NO BEST SPOT")
            action = self.tryBuildBestRoad(mappe, False)
            if action is not None:
                return action

    def favorRoad(self, mappe, infoJoueurs):

        chemin = self.chemin(mappe)

        if chemin[1] >= 5 and chemin[0] >= 2:
            return False

        armee = self.armee(mappe, infoJoueurs)

        if armee[1] >= 3 and armee[0] >= 1:
            return True

        return chemin[0] > armee[0]

    def chemin(self, mappe):
        maxChemin = 0
        idxJoueur = 0 if self._id <> 0 else 1
        curChemin = mappe.cheminPlusLong(idxJoueur)

        myChemin = mappe.cheminPlusLong(self._id)

        while curChemin > 0:

            if idxJoueur <> self._id and curChemin > maxChemin:
                maxChemin = curChemin

            idxJoueur += 1
            curChemin = mappe.cheminPlusLong(idxJoueur)

        diffChemin = myChemin - maxChemin

        return (diffChemin, myChemin)

    def armee(self, mappe, infoJoueurs):
        totalArmee = 0
        maxArmee = 0
        idxJoueur = 0 if self._id <> 0 else 1
        curArmee = infoJoueurs[idxJoueur][2]

        myArmee = infoJoueurs[self._id][2]

        totalArmee += curArmee + myArmee

        for idxJoueur in range(1,len(infoJoueurs)):

            if idxJoueur <> self._id and curArmee > maxArmee:
                maxArmee = curArmee

            curArmee = infoJoueurs[idxJoueur][2]
            totalArmee += curArmee

        diffArmee = myArmee - maxArmee

        return (diffArmee, myArmee, )

    def shouldBuildRoad(self, mappe):
        chemin = self.chemin(mappe)
        if (chemin[1] >= 5 and chemin[0] >= 2) or chemin[0] <= -4:
            print("No more cards")
        return not ((chemin[1] >= 5 and chemin[0] >= 2) or chemin[0] <= -4)

    def shouldBuyCard(self,mappe,infoJoueurs):
        armee = self.armee(mappe, infoJoueurs)
        if (armee[1] >= 3 and armee[0] >= 1):
            print("No more cards")

        return not (armee[1] >= 3 and armee[0] >= 1)


        
        
        
        

                
            
        
        
        
        
        
                    
                


