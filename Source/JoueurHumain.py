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

class Commodity:
    ROAD = 0
    SETTLEMENT = 1
    CITY = 2
    CARD = 3

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
        self.modeColonieRoute = True
        self.phase = "COLONIEROUTE"
        self.constructionOuAchat = "COLONIE"
        self.valeurGeneralePrecedente = 100

        self.valeurActionEchanger = 100  #on assigne une valeur à chaque action
        self.valeurActionVille = 100
        self.valeurActionColonie = 100
        self.valeurActionRoute = 101
        self.valeurActionAcheterCarte = 100
        self.valeurActionJouerCarteChevalier = 100

        self.strategy = Strategy.ROADS
        self.state = State.EXPAND

        self.incomeStats = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.resourceValues = [1, 1.2, 1.1, 0.9, 0.8] #BLÉ, ARGILE, BOIS, MINÉRAL, LAINE

        #tableau des valeurs des actions
        self.valeursActions = [self.valeurActionEchanger, self.valeurActionVille, self.valeurActionColonie, self.valeurActionRoute, self.valeurActionAcheterCarte, self.valeurActionJouerCarteChevalier]

        #tableau des actions du tour precedent
        self.actionsPrecedentes = []


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

        self.state = self.chooseState()

        #TODO: STATES
        if(self.state == State.EXPAND):
            print("1")
            spot = self.getBestColonySpot(mappe)
            if spot is not None:
                print ("SPOT: " + str(spot._id))
                bestNeighbor = self.getBestNeighbor(spot, mappe)
                if bestNeighbor is not None:
                    print("BEST NEIGHBOR: " + str(bestNeighbor._id))
                    action = self.tryBuildCommodity(Action.AJOUTER_ROUTE, [spot._id, bestNeighbor._id])
                    if action is not None:
                        print(str(action))
                        return action
                else:
                    print("NO BEST NEIGHBOR")
                    action = self.tryBuildCommodity(Action.AJOUTER_COLONIE, [spot._id])
                    if action is not None:
                        print("BUILD ROAD: " + str(action))
                        return action
            else:
                print("NO BEST SPOT")
                action = self.tryBuildBestRoad(mappe)
                if action is not None:
                    print(str(action))
                    return action
            print("TRY CITY")
            action = self.tryBuildBestCity()
            if action is not None:
                print(str(action))
                return action

            print("TRY CARTE")
            action = self.tryBuildCommodity(Action.ACHETER_CARTE, [])
            if action is not None:
                print(str(action))
                return action

            if self.peutJouerCarteChevalier():
                return (Action.JOUER_CARTE_CHEVALIER, [])

            self.gererExtra()

                
        print 'TERMINER'
        return Action.TERMINER

    def gererExtra(self):
        pass

    def tryBuildBestCity(self):
        pass

    def tryBuildBestRoad(self, mappe):

        bestRoad = None
        bestRoadOrigin = None
        bestRoadScore = 0

        for i in mappe.obtenirToutesLesIntersections():
            if mappe._accesRoute(i._id,self._id):
                potentialRoad = self.trouverMeilleureIntersectionRoute(i, mappe)

                if potentialRoad[1] > bestRoadScore:
                    bestRoad = potentialRoad[0]
                    bestRoadScore = potentialRoad[1]
                    bestRoadOrigin = i

            if bestRoad is not None:
                return self.tryBuildCommodity(Action.AJOUTER_ROUTE,[bestRoadOrigin._id, bestRoad._id])

        return None

    def tryBuildCommodity(self, action, data):
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

        print("RESSOURCE DIFF " + str(action) + " : " + str(ressourceDiff))

        if not any(t < 0 for t in ressourceDiff):
            if data is None:
                return action
            else:
                return (action,data)

        priorityList = [Ressource.ARGILE, Ressource.BOIS, Ressource.BLE, Ressource.LAINE, Ressource.MINERAL]

        firstTrade = None

        for r in priorityList:
            if(ressourceDiff[r] >= 0):
                continue
            print("MISSING " + str(r))

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

                    print("CAN TRADE " + str(r2))
                    while(ressourceDiff[r] < 0 and ressourceDiff[r2] >= nbTrade):
                        print("TRADE " + str(nbTrade) + " " + str(r2) + " for 1 " + str(r))
                        if firstTrade is None:
                            firstTrade = (Action.ECHANGER_RESSOURCES,[nbTrade, r2, r])
                        ressourceDiff[r] += 1
                        ressourceDiff[r2] -= nbTrade
                        print("RESSOURCE DIFF: " + str(ressourceDiff))

        print("END: " + str(ressourceDiff))

        if not any(t < 0 for t in ressourceDiff):
            print("ON ECHANGE: " + str(firstTrade))
            return firstTrade

        print("FAIL " + str(action))
        return None

    def getBestNeighbor(self, intersection, mappe):

        maxScore = 0
        meilleureIntersection = 0

        for i in intersection.obtenirVoisins():
            if mappe.peutConstruireOccupation(i._id, self._id): #si on peut poser une colonie sur l'intersection
                if not i.occupe():
                    score = self.calculerScoreIntersectionColonie(i, mappe)

                    if(score > maxScore):
                        maxScore = score
                        meilleureIntersection = i

        if maxScore > 1.5 * self.calculerScoreIntersectionColonie(intersection, mappe):
            return meilleureIntersection

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

    #TODO: STATES
    def chooseState(self):
       return State.EXPAND

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

        print("SCORE INTERSECTION " + str(intersection._id) + " : " + str(score))

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

        

    def deciderCommerce(self):

        ressourceEnManque = self.ressourceEnManque()

        if ressourceEnManque != False:
            
            if ressourceEnManque == Ressource.BOIS:
                
                if self.choisirEchange(Ressource.MINERAL, Ressource.BOIS) != False:
                    return self.choisirEchange(Ressource.MINERAL,Ressource.BOIS)

                if self.choisirEchange(Ressource.LAINE, Ressource.BOIS) != False:
                    return self.choisirEchange(Ressource.LAINE, Ressource.BOIS)

                if self.choisirEchange(Ressource.BLE, Ressource.BOIS) != False:
                    return self.choisirEchange(Ressource.BLE, Ressource.BOIS)

                if self.choisirEchange(Ressource.ARGILE, Ressource.BOIS) != False:
                    return self.choisirEchange(Ressource.ARGILE, Ressource.BOIS)
                
                return False
                
            elif ressourceEnManque == Ressource.ARGILE:

                if self.choisirEchange(Ressource.MINERAL, Ressource.ARGILE) != False:
                    return self.choisirEchange(Ressource.MINERAL,Ressource.ARGILE)

                if self.choisirEchange(Ressource.LAINE, Ressource.ARGILE) != False:
                    return self.choisirEchange(Ressource.LAINE, Ressource.ARGILE)

                if self.choisirEchange(Ressource.BLE, Ressource.ARGILE) != False:
                    return self.choisirEchange(Ressource.BLE, Ressource.ARGILE)

                if self.choisirEchange(Ressource.BOIS, Ressource.ARGILE) != False:
                    return self.choisirEchange(Ressource.BOIS, Ressource.ARGILE)

                return False
                
            elif ressourceEnManque == Ressource.MINERAL:

                if self.choisirEchange(Ressource.BOIS, Ressource.MINERAL) != False:
                    return self.choisirEchange(Ressource.BOIS,Ressource.MINERAL)

                if self.choisirEchange(Ressource.ARGILE, Ressource.MINERAL) != False:
                    return self.choisirEchange(Ressource.ARGILE, Ressource.MINERAL)

                return False
                                        

            elif ressourceEnManque == Ressource.BLE:

                if self.choisirEchange(Ressource.BOIS, Ressource.BLE) != False:
                    return self.choisirEchange(Ressource.BOIS, Ressource.BLE)
                
                if self.choisirEchange(Ressource.LAINE, Ressource.BLE) != False:
                    return self.choisirEchange(Ressource.LAINE, Ressource.BLE)

                if self.choisirEchange(Ressource.ARGILE, Ressource.BLE) != False:
                    return self.choisirEchange(Ressource.ARGILE, Ressource.BLE)

                if self.choisirEchange(Ressource.MINERAL, Ressource.BLE) != False:
                    return self.choisirEchange(Ressource.MINERAL, Ressource.BLE)

                return False
            
            elif ressourceEnManque == Ressource.LAINE:

                if self.choisirEchange(Ressource.MINERAL, Ressource.LAINE) != False:
                    return self.choisirEchange(Ressource.MINERAL, Ressource.LAINE)

                if self.choisirEchange(Ressource.ARGILE, Ressource.LAINE) != False:
                    return self.choisirEchange(Ressource.ARGILE, Ressource.LAINE)

                return False
            
        return False
                            
    
    def ressourceEnManque(self):

        if self.quantiteRessources(Ressource.BLE) == 0:
            return Ressource.BLE
        if self.quantiteRessources(Ressource.ARGILE) == 0:
            return Ressource.ARGILE
        if self.quantiteRessources(Ressource.BOIS) == 0:
            return Ressource.BOIS
        if self.quantiteRessources(Ressource.LAINE) == 0:
            return Ressource.LAINE
        if self.quantiteRessources(Ressource.MINERAL) == 0:
            return Ressource.MINERAL
        

        return False


    def choisirEchange(self,ressourceOfferte,ressourceDemandee):
        
        if self.quantiteRessources(ressourceOfferte) < 2:
            return False
        
        elif self.quantiteRessources(ressourceOfferte) == 2:

            if ressourceOfferte in self._peutEchanger:
                return [2, ressourceOfferte, ressourceDemandee]           
            
        elif self.quantiteRessources(ressourceOfferte) >= 3 and self.quantiteRessources(ressourceOfferte) < 5:

            if ressourceOfferte in self._peutEchanger:
                return [2, ressourceOfferte, ressourceDemandee]

            if self._possedePortGenerique:
                return [3, ressourceOfferte, ressourceDemandee]
            

        elif self.quantiteRessources(ressourceOfferte) >= 5:

            if ressourceOfferte in self._peutEchanger:
                return [2, ressourceOfferte, ressourceDemandee]

            if self._possedePortGenerique:
                return [3, ressourceOfferte, ressourceDemandee]

            return [4, ressourceOfferte, ressourceDemandee]
        

        return False

    def echangesPossibles(self):

        echangesPossibles = []
        
        
        if self._peutEchanger:

            
            if Ressource.BOIS in self._peutEchanger:
                
                if self.quantiteRessources(Ressource.BOIS) >= 2:
                    echangesPossibles.append([2, Ressource.BOIS, Ressource.ARGILE])
                    echangesPossibles.append([2, Ressource.BOIS, Ressource.MINERAL])
                    echangesPossibles.append([2, Ressource.BOIS, Ressource.BLE])
                    echangesPossibles.append([2, Ressource.BOIS, Ressource.LAINE])

            if Ressource.ARGILE in self._peutEchanger:
                
                if self.quantiteRessources(Ressource.ARGILE) >= 2:
                    echangesPossibles.append([2, Ressource.ARGILE, Ressource.BOIS])
                    echangesPossibles.append([2, Ressource.ARGILE, Ressource.MINERAL])
                    echangesPossibles.append([2, Ressource.ARGILE, Ressource.BLE])
                    echangesPossibles.append([2, Ressource.ARGILE, Ressource.LAINE])

            if Ressource.MINERAL in self._peutEchanger:
                
                if self.quantiteRessources(Ressource.MINERAL) >= 2:
                    echangesPossibles.append([2, Ressource.MINERAL, Ressource.BOIS])
                    echangesPossibles.append([2, Ressource.MINERAL, Ressource.ARGILE])
                    echangesPossibles.append([2, Ressource.MINERAL, Ressource.BLE])
                    echangesPossibles.append([2, Ressource.MINERAL, Ressource.LAINE])

            if Ressource.BLE in self._peutEchanger:
                
                if self.quantiteRessources(Ressource.BLE) >= 2:
                    echangesPossibles.append([2, Ressource.BLE, Ressource.BOIS])
                    echangesPossibles.append([2, Ressource.BLE, Ressource.ARGILE])
                    echangesPossibles.append([2, Ressource.BLE, Ressource.MINERAL])
                    echangesPossibles.append([2, Ressource.BLE, Ressource.LAINE])

            if Ressource.LAINE in self._peutEchanger:
                
                if self.quantiteRessources(Ressource.LAINE) >= 2:
                    echangesPossibles.append([2, Ressource.LAINE, Ressource.BOIS])
                    echangesPossibles.append([2, Ressource.LAINE, Ressource.ARGILE])
                    echangesPossibles.append([2, Ressource.LAINE, Ressource.MINERAL])
                    echangesPossibles.append([2, Ressource.LAINE, Ressource.BLE])
                

        if self._possedePortGenerique:

            if self.quantiteRessources(Ressource.BOIS) >= 3:
                echangesPossibles.append([3, Ressource.BOIS, Ressource.ARGILE])
                echangesPossibles.append([3, Ressource.BOIS, Ressource.MINERAL])
                echangesPossibles.append([3, Ressource.BOIS, Ressource.BLE])
                echangesPossibles.append([3, Ressource.BOIS, Ressource.LAINE])

            if self.quantiteRessources(Ressource.ARGILE) >= 3:
                echangesPossibles.append([3, Ressource.ARGILE, Ressource.BOIS])
                echangesPossibles.append([3, Ressource.ARGILE, Ressource.MINERAL])
                echangesPossibles.append([3, Ressource.ARGILE, Ressource.BLE])
                echangesPossibles.append([3, Ressource.ARGILE, Ressource.LAINE])

            if self.quantiteRessources(Ressource.MINERAL) >= 3:
                echangesPossibles.append([3, Ressource.MINERAL, Ressource.BOIS])
                echangesPossibles.append([3, Ressource.MINERAL, Ressource.ARGILE])
                echangesPossibles.append([3, Ressource.MINERAL, Ressource.BLE])
                echangesPossibles.append([3, Ressource.MINERAL, Ressource.LAINE])

            if self.quantiteRessources(Ressource.BLE) >= 3:
                echangesPossibles.append([3, Ressource.BLE, Ressource.BOIS])
                echangesPossibles.append([3, Ressource.BLE, Ressource.ARGILE])
                echangesPossibles.append([3, Ressource.BLE, Ressource.MINERAL])
                echangesPossibles.append([3, Ressource.BLE, Ressource.LAINE])

            if self.quantiteRessources(Ressource.LAINE) >= 3:
                echangesPossibles.append([3, Ressource.LAINE, Ressource.BOIS])
                echangesPossibles.append([3, Ressource.LAINE, Ressource.ARGILE])
                echangesPossibles.append([3, Ressource.LAINE, Ressource.MINERAL])
                echangesPossibles.append([3, Ressource.LAINE, Ressource.BLE])
            

        if self.quantiteRessources(Ressource.BOIS) >= 4:
            echangesPossibles.append([4, Ressource.BOIS, Ressource.ARGILE])
            echangesPossibles.append([4, Ressource.BOIS, Ressource.MINERAL])
            echangesPossibles.append([4, Ressource.BOIS, Ressource.BLE])
            echangesPossibles.append([4, Ressource.BOIS, Ressource.LAINE])

        if self.quantiteRessources(Ressource.ARGILE) >= 4:
            echangesPossibles.append([4, Ressource.ARGILE, Ressource.BOIS])
            echangesPossibles.append([4, Ressource.ARGILE, Ressource.MINERAL])
            echangesPossibles.append([4, Ressource.ARGILE, Ressource.BLE])
            echangesPossibles.append([4, Ressource.ARGILE, Ressource.LAINE])

        if self.quantiteRessources(Ressource.MINERAL) >= 4:
            echangesPossibles.append([4, Ressource.MINERAL, Ressource.BOIS])
            echangesPossibles.append([4, Ressource.MINERAL, Ressource.ARGILE])
            echangesPossibles.append([4, Ressource.MINERAL, Ressource.BLE])
            echangesPossibles.append([4, Ressource.MINERAL, Ressource.LAINE])

        if self.quantiteRessources(Ressource.BLE) >= 4:
            echangesPossibles.append([4, Ressource.BLE, Ressource.BOIS])
            echangesPossibles.append([4, Ressource.BLE, Ressource.ARGILE])
            echangesPossibles.append([4, Ressource.BLE, Ressource.MINERAL])
            echangesPossibles.append([4, Ressource.BLE, Ressource.LAINE])

        if self.quantiteRessources(Ressource.LAINE) >= 4:
            echangesPossibles.append([4, Ressource.LAINE, Ressource.BOIS])
            echangesPossibles.append([4, Ressource.LAINE, Ressource.ARGILE])
            echangesPossibles.append([4, Ressource.LAINE, Ressource.MINERAL])
            echangesPossibles.append([4, Ressource.LAINE, Ressource.BLE])


        if echangesPossibles:
            return echangesPossibles

        return False

            

    def deciderConstructionAchat(self,mappe):


        if not self._peutEchanger:
            if not self._possedePortGenerique:
                versPort = self.allerVersPort(mappe)

                if versPort != False:
                    return versPort

        self.constructionOuAchat = "VILLE"

        futureVille = self.choisirFutureVille(mappe)

        if futureVille != False:
            return futureVille._id

        self.constructionOuAchat = "COLONIE"

        futureColonie = self.choisirFutureColonie(mappe)

        if futureColonie != False:
            return futureColonie._id

        self.constructionOuAchat = "ROUTE"
        futureRoute = self.choisirFutureRoute(mappe)

        if futureRoute != False:
            return futureRoute

        self.constructionOuAchat = "ACHETER CARTE"

        if self.possibleAcheterCarte():
            return (Action.ACHETER_CARTE,[])

        self.constructionOuAchat = "RIEN"

        return False

        

    def choisirFutureVille(self,mappe):
        
        colonies = self.possibleAjouterVille(mappe)
        meilleureValeurProduction = 0
        futureVille = 0

        if colonies != False:
            
            for i in colonies:
                
                valeurProduction = 0      #demarche pour trouver la meilleure valeur de production

                for t in i.obtenirTerritoiresVoisins():
                    valeurProduction += self.obtenirValeurProductionChiffre(t._valeur)

                if valeurProduction > meilleureValeurProduction:
                    meilleureValeurProduction = valeurProduction
                    futureVille = i._id

            return futureVille

        return False

    

    def possibleAjouterVille(self,mappe):

        colonies = []

        if self.quantiteRessources(Ressource.BLE) >= 2 and self.quantiteRessources(Ressource.MINERAL) >= 3:
            for i in mappe.obtenirToutesLesIntersections():
                if i.occupe() and i.obtenirOccupant() == self._id and i.occupation() == 1:
                    colonies.append(i)

        if colonies:
            return colonies
        
        else:
            return False



    def choisirFutureColonie(self,mappe):

        possiblesIntersections = self.possibleAjouterColonie(mappe)

        meilleureValeurProduction = 0
        futureColonie = 0

        if possiblesIntersections != False:

            for i in possiblesIntersections:

                valeurProduction = 0

                for t in i.obtenirTerritoiresVoisins():
                    valeurProduction += self.obtenirValeurProductionChiffre(t._valeur)

                if valeurProduction > meilleureValeurProduction:
                    meilleureValeurProduction = valeurProduction
                    futureColonie = i._id

            if futureColonie != 0:
                return futureColonie

        return False

                    
                                                                                        
    def possibleAjouterColonie(self,mappe):

        possiblesIntersections = []
        
        if self.quantiteRessources(Ressource.BLE) >= 1 and self.quantiteRessources(Ressource.ARGILE) >= 1 and self.quantiteRessources(Ressource.BOIS) >= 1 and self.quantiteRessources(Ressource.LAINE) >= 1:
            for i in mappe.obtenirToutesLesIntersections():
                if mappe.peutConstruireOccupation(i._id,self._id):
                    if not i.occupe():
                        if i!=None:
                            possiblesIntersections.append(i)

        if possiblesIntersections:
            return possiblesIntersections
                
        return False

    

    def choisirFutureRoute(self,mappe):

        possiblesRoutes = []
        meilleureValeurProduction = 0
        futureRoute = 0

        if self.possibleAjouterRoute(mappe):
            for i in mappe.obtenirToutesLesIntersections():
                if mappe._accesRoute(i._id,self._id):
                    for j in i.obtenirVoisins():
                        if mappe.peutConstruireRoute(i._id,j._id,self._id):
                            if not mappe.intersectionPossedeRoute(i._id,j._id):
                                possiblesRoutes.append([i._id,j._id])

        if possiblesRoutes:
            
            for r in possiblesRoutes:
                
                valeurProduction = 0

                for t in r[1].obtenirTerritoiresVoisins():
                    valeurProduction += self.obtenirValeurProductionChiffre(t._valeur)

                if valeurProduction > meilleureValeurProduction:
                    meilleureValeurProduction = valeurProduction
                    futureRoute = [r[0],r[1]]

            return futureRoute
                

        return False
                            
                
        

    def possibleAjouterRoute(self,mappe):

        emplacementsPossibles = []
        
        if self.quantiteRessources(Ressource.BOIS) >= 1 and self.quantiteRessources(Ressource.ARGILE) >= 1:
            for i in mappe.obtenirToutesLesIntersections():
                for j in i.obtenirVoisins():
                    if mappe.peutConstruireRoute(i._id,j._id,self._id):
                        if [j._id,i._id] not in emplacementsPossibles:
                            emplacementsPossibles.append([i._id,j._id])

        if emplacementsPossibles:
            return emplacementsPossibles
            
        return False
            

    def possibleAcheterCarte(self):
        
        if self.quantiteRessources(Ressource.BLE) >= 1 and self.quantiteRessources(Ressource.LAINE) >= 1 and self.quantiteRessources(Ressource.MINERAL) >= 1:
            return True

        else:
            return False
    

                 
            
            


                
            
            
            
            
        




        
        
        
        

                
            
        
        
        
        
        
                    
                


