#!/usr/bin/python
#-*- coding: latin-1 -*-

# Contr�leur du jeu de Catane
#
# Date: 22 mars  2014
#
# Auteur: Michel Gagnon



import sys
import getopt
import random
import math
import urllib
import urllib2
import copy
import os
import time
from decimal import Decimal
from Joueur import *
from Mappe import *
from Cartes import *
from FabriqueJoueur import *
from Action import *
from multiprocessing import Process, Pipe, Lock

from Sender import *

fabrique = FabriqueJoueur()


class Controleur(object):
    def __init__(self,listeJoueurs,debug=False):
        self._debug = debug
        random.seed()
        self._nombreJoueurs = len(listeJoueurs)

        if self._debug:
            self._numeroSequenceDes = 0
            self._mappe = Mappe(['foret','champ','colline','champ','colline','montagne','pre','foret','montagne','desert','foret','colline','pre','champ','montagne','pre','pre','foret','champ'])
            self._paquetCartes = Cartes(True)
        else:
            random.shuffle(listeJoueurs)
            self._mappe = Mappe()
            self._paquetCartes = Cartes()

        self._joueurs = []
        self._longueurCheminPlusLong = 1
        self._joueurAyantCheminPlusLong = None
        self._armeePlusPuissante = 0
        self._joueurAyantArmeePlusPuissante = None

        for i in range(self._nombreJoueurs):
            self._joueurs.append(fabrique.creerJoueur(listeJoueurs[i],i))


    def jouer(self):
        # Premier tour: chaque joueur place une colonie et une route
        for i in range(self._nombreJoueurs):
            print 'Premier tour,', self._joueurs[i].nom()
            try:
                (positionColonie, extremiteRoute) = self._joueurs[i].premierTour(self._mappe)
                self._mappe._ajouterOccupationInitiale(positionColonie,Occupation.COLONIE,i)
                self._joueurs[i].ajusterCapaciteEchange(self._mappe.obtenirIntersection(positionColonie))
                self._mappe._ajouterRoute(positionColonie, extremiteRoute, i)
                print 'Occupation plac�e avec succ�s'
            except RuntimeError as e:
                print 'ERREUR:', e

        # Deuxi�me tour: en ordre inverse, chaque joueur place une seconde colonie et une seconde route
        for i in range(self._nombreJoueurs-1,-1,-1):
            print 'Deuxi�me  tour,', self._joueurs[i].nom()
            try:
                (positionColonie, extremiteRoute) = self._joueurs[i].deuxiemeTour(self._mappe)
                self._mappe._ajouterOccupationInitiale(positionColonie,Occupation.COLONIE,i)
                self._joueurs[i].ajusterCapaciteEchange(self._mappe.obtenirIntersection(positionColonie))
                self._mappe._ajouterRoute(positionColonie, extremiteRoute, i)
                print 'Occupation plac�e avec succ�s'
                
                # Distribuer les ressources initiales
                self._mappe._distribuerRessourcesInitiales(self._joueurs[i],positionColonie)

            except RuntimeError as e:
                print 'ERREUR:', e



        print '�tat apr�s le placement initial:'
        self._mappe.afficher()

        self._afficherEtatJoueurs()

        # � partir de maintenant on commence les tours r�guliers
        joueurCourant = 0
        numeroTour = 0
        while not self._joueurGagnant() and numeroTour < 1000:
            numeroTour += 1
            valeur = self._lancerDes()

            print 'Tour', numeroTour
            print 'Valeur des d�s',valeur

            # Si la valeur des d�s est 7, chaque joueur poss�dant plus de 7 cartes doit en discarter la 
            # moiti� et le joueur courant doit d�placer les voleurs
            if (valeur == 7):
                for joueur in self._joueurs:
                    if joueur.nombreRessources() > 7:
                        print joueur.nom(),"se fait voler"
                        quantiteVolee = joueur.nombreRessources() // 2
                        joueur.volerRessources(quantiteVolee)

                if self._debug:
                    (positionVoleurs,joueurVole) = self._joueurs[joueurCourant].jouerVoleurs(self._mappe,self._infoJoueurs())
                else:
                    (positionVoleurs,joueurVole) = self._joueurs[joueurCourant].jouerVoleurs(self._mappe,self._infoJoueurs())

                if 1 <= positionVoleurs and positionVoleurs <= 19 and joueurVole in range(self._nombreJoueurs):
                    self._mappe._deplacerVoleurs(positionVoleurs)
                    print self._joueurs[joueurCourant].nom(), 'vole', self._joueurs[joueurVole].nom()
                    ressourceVolee = self._joueurs[joueurVole].pigerRessourceAleatoirement()
                    if ressourceVolee == None:
                        print "ERREUR : Ce joueur ne poss�de aucune ressource"
                    else:
                        self._joueurs[joueurCourant].ajouterRessources(ressourceVolee,1)

            # Sinon, chaque joueur re�oit les ressources auxquelles il a droit
            else:
                ressources = self._mappe._distribuerRessources(valeur)
                for (j,r) in ressources:
                    self._joueurs[j].ajouterRessources(r,ressources[(j,r)])

            # On rend jouables les cartes chevalier recues dans le tour pr�c�dent
            self._joueurs[joueurCourant].activerChevaliers()

            print 'Etat des joueurs apr�s distribution des ressources:'
            for i in range(self._nombreJoueurs):
                self._joueurs[i].afficher()
            print 
            print self._joueurs[joueurCourant].nom(), '[', joueurCourant, '] joue'

            # On ex�cute toutes les actions choisies par le joueur courant
            nombreActions = 0
            if self._debug:
                action = self._joueurs[joueurCourant].choisirAction(self._mappe,self._infoJoueurs(),self._paquetCartes.vide(),self._numeroSequenceDes)
            else:
                action = self._joueurs[joueurCourant].choisirAction(self._mappe,self._infoJoueurs(),self._paquetCartes.vide())

            while action != Action.TERMINER and nombreActions < 50:
                self._executer(action,joueurCourant)
                if self._debug:
                    action = self._joueurs[joueurCourant].choisirAction(self._mappe,self._infoJoueurs(),self._paquetCartes.vide(),self._numeroSequenceDes)
                else:
                    action = self._joueurs[joueurCourant].choisirAction(self._mappe,self._infoJoueurs(),self._paquetCartes.vide())
                nombreActions += 1

            # On passe au joueur suivant
            print "�tat � la fin du tour"
            self._mappe.afficher()
            self._afficherEtatJoueurs()
            joueurCourant = (joueurCourant+1) % self._nombreJoueurs


    # Retourne une liste contenant un triplet (pv, car, ch) pour chaque joueur
    #  o� pv = nombre de points de victoire (excluant les cartes de points de victoire cach�es)
    #     car = nombre de cartes ressources que le joueur a en sa possession
    #     ch = nombre de cartes chevalier jou�es
    def _infoJoueurs(self):
        infoJoueurs = []
        for i in range(self._nombreJoueurs):
            infoJoueurs.append((self._joueurs[i].nombrePointsVictoireVisibles(), 
                                self._joueurs[i].nombreCartesRessources(), 
                                self._joueurs[i].nombreChevaliers()))
        return infoJoueurs

    def _afficherEtatJoueurs(self):
        for i in range(self._nombreJoueurs):
            self._joueurs[i].afficher()


    def _joueurGagnant(self):
        for j in range(self._nombreJoueurs):
            if self._joueurs[j].nombrePointsVictoire() >= 10:
                print self._joueurs[j].nom(),"a gagn� la partie"
                return True
        return False


    def _executer(self,(action,donnees),joueurCourant):
        if action == Action.ACHETER_CARTE:
            print "ACHETER CARTE"
            if (self._joueurs[joueurCourant].quantiteRessources(Ressource.LAINE) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.MINERAL) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.BLE) >= 1):
                if self._paquetCartes.vide():
                    print "ERREUR: Paquet de cartes vide"
                else:
                    self._joueurs[joueurCourant].retirerRessources(Ressource.LAINE,1)
                    self._joueurs[joueurCourant].retirerRessources(Ressource.MINERAL,1)
                    self._joueurs[joueurCourant].retirerRessources(Ressource.BLE,1)            
                    self._joueurs[joueurCourant].ajouterCarte(self._paquetCartes.pigerCarte())
            else:
                print "ERREUR: Pas assez de ressources pour acheter une carte"

        elif action == Action.AJOUTER_COLONIE:
            print "AJOUTER COLONIE"
            if (self._joueurs[joueurCourant].quantiteRessources(Ressource.BOIS) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.ARGILE) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.BLE) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.LAINE) >= 1):
                try:
                    self._mappe._ajouterOccupation(donnees[0],Occupation.COLONIE,joueurCourant)
                    self._joueurs[joueurCourant].ajusterCapaciteEchange(self._mappe.obtenirIntersection(donnees[0]))
                    self._joueurs[joueurCourant].retirerRessources(Ressource.BOIS,1)
                    self._joueurs[joueurCourant].retirerRessources(Ressource.ARGILE,1)
                    self._joueurs[joueurCourant].retirerRessources(Ressource.BLE,1)     
                    self._joueurs[joueurCourant].retirerRessources(Ressource.LAINE,1)     
                    self._joueurs[joueurCourant].augmenterPointsVictoire(1)
                except RuntimeError as e:
                        print 'ERREUR:',e
            else:
                print "ERREUR: Pas assez de ressources pour construire une colonie"


        elif action == Action.AJOUTER_VILLE:
            print "AJOUTER VILLE"
            if (self._joueurs[joueurCourant].quantiteRessources(Ressource.BLE) >= 2 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.MINERAL) >= 3):
                   try:
                       self._mappe._ajouterOccupation(donnees[0],Occupation.VILLE,joueurCourant)
                       self._joueurs[joueurCourant].retirerRessources(Ressource.BLE,2)     
                       self._joueurs[joueurCourant].retirerRessources(Ressource.MINERAL,3)     
                       self._joueurs[joueurCourant].augmenterPointsVictoire(1)
                   except RuntimeError as e:
                       print 'ERREUR:',e
            else:
                print "ERREUR: Pas assez de ressources pour construire une ville"


        elif action == Action.AJOUTER_ROUTE:  
            print "AJOUTER ROUTE"                        
            if (self._joueurs[joueurCourant].quantiteRessources(Ressource.BOIS) >= 1 and
                self._joueurs[joueurCourant].quantiteRessources(Ressource.ARGILE) >= 1):
                   try:
                       self._mappe._ajouterRoute(donnees[0],donnees[1],joueurCourant)
                       self._joueurs[joueurCourant].retirerRessources(Ressource.BOIS,1)
                       self._joueurs[joueurCourant].retirerRessources(Ressource.ARGILE,1)
                       self._attribuerPointsRoutePlusLongue(joueurCourant)
                   except RuntimeError as e:
                       print 'ERREUR:',e
            else:
                print "ERREUR: Pas assez de ressources pour construire une route"

 
        elif action == Action.JOUER_CARTE_CHEVALIER:
            print "JOUER CARTE CHEVALIER"
            try:
                self._joueurs[joueurCourant].jouerCarteChevalier()
                self._attribuerPointsArmeePlusPuissante(joueurCourant)
                self._mappe._deplacerVoleurs(donnees[0])
                joueurVole = donnees[1]
                if joueurVole in  [v.obtenirOccupant() for v in self._mappe.obtenirTerritoire(donnees[0]).obtenirVoisins()]:
                    ressourceVolee = self._joueurs[joueurVole].pigerRessourceAleatoirement()
                    self._joueurs[joueurCourant].ajouterRessources(ressourceVolee,1)
            except Exception as e:
                print 'ERREUR:', e

        elif action == Action.ECHANGER_RESSOURCES:
            print "ECHANGER"
            self._echanger(joueurCourant,donnees[0],donnees[1],donnees[2])

        else:
            pass # Action invalide

    # On v�rifie si le joueur courant a maintenant le chemin le plus long 
    # Si c'est le cas, c'est lui qui r�cup�re les 2 points de victoire
    def _attribuerPointsRoutePlusLongue(self,joueurCourant):
        plusLongCheminJoueurCourant = self._mappe.cheminPlusLong(joueurCourant)
        if plusLongCheminJoueurCourant < 5:
            return
        if plusLongCheminJoueurCourant > self._longueurCheminPlusLong:
            ancienJoueur = self._joueurAyantCheminPlusLong
            if ancienJoueur != None:
                self._joueurs[ancienJoueur].diminuerPointsVictoire(2)
            self._joueurAyantCheminPlusLong = joueurCourant
            self._longueurCheminPlusLong = plusLongCheminJoueurCourant
            self._joueurs[joueurCourant].augmenterPointsVictoire(2)

    # On v�rifie si le joueur courant a maintenant l'arm�ee la plus puissante
    # Si c'est le cas, c'est lui qui r�cup�re les 2 points de victoire                
    def _attribuerPointsArmeePlusPuissante(self,joueurCourant):
        if self._joueurs[joueurCourant].nombreChevaliers() < 3:
            return
        if self._joueurs[joueurCourant].nombreChevaliers() > self._armeePlusPuissante:
            ancienJoueur = self._joueurAyantArmeePlusPuissante
            if ancienJoueur != None:
                self._joueurs[ancienJoueur].diminuerPointsVictoire(2)
            self._joueurAyantArmeePlusPuissante = joueurCourant
            self._armeePlusPuissante = self._joueurs[joueurCourant].nombreChevaliers()
            self._joueurs[joueurCourant].augmenterPointsVictoire(2)            


    def _echanger(self,joueurCourant,quantite,offre,demande):
        if quantite == 4 and self._joueurs[joueurCourant].peutEchangerBanque(offre):
            self._joueurs[joueurCourant].retirerRessources(offre,4)    
            self._joueurs[joueurCourant].ajouterRessources(demande,1)    
        elif quantite == 3 and self._joueurs[joueurCourant].peutEchangerPortGenerique(offre):
            self._joueurs[joueurCourant].retirerRessources(offre,3)    
            self._joueurs[joueurCourant].ajouterRessources(demande,1)    
        elif quantite == 2 and self._joueurs[joueurCourant].peutEchangerPortSpecialise(offre):
            self._joueurs[joueurCourant].retirerRessources(offre,2)    
            self._joueurs[joueurCourant].ajouterRessources(demande,1) 
        else:
            print "ERREUR : �change impossible, offre insufisante" 



    def _lancerDes(self):
        if self._debug:
            sequence = [6,10,9,2,6,5,9,7,2,4,4,11,12,6,12,6,9,8,8,8,10,2,4,8,9,9,11,2,2,2,8,9,8,9,4,6,2,2,3,4,5,6,8,9,10,11,10,10,10,4,8,2,4,2,2,2,2,2,2,2,4,4,4,4,4,11,2,4,2,4,2,3,11,3,11]
            v = sequence[self._numeroSequenceDes]
            self._numeroSequenceDes += 1
			# On reprend la sequence des Des depuis le debut 
            if (self._numeroSequenceDes ==  len(sequence)):
                self._numeroSequenceDes = 0				
            return v
        else:
            d1 = int(math.ceil(random.random()*6))
            d2 = int(math.ceil(random.random()*6))
            return d1+d2

    def setValuesForAI(self, joueur, values):
        self._joueurs[joueur].setValues(values)

    def obtenirInfoJoueurs(self):
        a = []
        for joueur in self._joueurs:
            a.append((joueur.id(),
                      joueur.estHumain,
                      joueur.nombrePointsVictoire(),
                      joueur.nombreCartesRessources(),
                      joueur.nombreChevaliers()
            ))

        return a



def runner(initConfig, parameter, fixval, min, max, step, lock, write_pipe):

    config = copy.deepcopy(initConfig)
    config[0] = fixval

    parameters = range(5)

    parameters.remove(parameter)

    pid = os.getpid()
    it = 0

    nbSteps = (max + step - min) / step

    totalSteps = math.pow(nbSteps, 4)

    while config[1] <= max:
        while config[2] <= max:
            while config[3] <= max:
                begin = time.mktime(time.gmtime())
                while config[4] <= max:
                    run_config(config, lock, write_pipe, 5)
                    # print "running config", config
                    config[4] += step
                    it += 1
                    # console_handle.write("Process " + str(pid) + " running iteration " + str(it) + os.linesep)
                config[4] = min
                config[3] += step

                end = time.mktime(time.gmtime())

                diff = end - begin

                eta = diff * math.pow(nbSteps, 3)
                pcent = it / totalSteps * 100

                remaining = eta - eta * it / totalSteps

                console_handle.write("Took " + str(diff) + " seconds to complete " + str(nbSteps) + os.linesep)
                console_handle.write("Total ETA " + str(eta) + os.linesep)
                console_handle.write("ETA " + str(remaining) + os.linesep)
                console_handle.write("Progress " + str(math.floor(pcent)) + "%" + os.linesep)

            config[3] = min
            config[2] += step
        config[2] = min
        config[1] += step

def run_config(resourceValues, lock, write_pipe, nb):
    for z in range(nb):
        # Game loop
        c = Controleur(['Humain','AI','AI','AI'])

        # Set values for each humain
        info = c.obtenirInfoJoueurs()
        for i in info:
            if i[1]:
                c.setValuesForAI(i[0], resourceValues)

        # Play
        c.jouer()

        # Get results
        info = c.obtenirInfoJoueurs()
        print info

        print 'pushing data',resourceValues
        push_data(resourceValues, info, lock, write_pipe)

def push_data(val, info, lock, write_pipe):
    lock.acquire()
    write_pipe.send((val, info))
    lock.release()

def get_top_100():
    url = 'http://step.polymtl.ca/~alexrose/catane/top100.txt'
    response = urllib2.urlopen(url=url, timeout=120)
    top = response.read()
    response.close()

    values = []

    for line in top.split('\n'):
        tup = eval(line)

        tup = list(tup)
        for i in range(5):
            x = Decimal(tup[i])
            x = round(x, 1)
            tup[i] = x
        tup = tuple(tup)
        values.append(tup)

    return values

def config_runner(configs, lock, write_pipe):
    for config in configs:
        run_config(config, lock, write_pipe, 5)
        print "Running configs", configs



# f = file('out.txt', 'w+')
f = file(os.devnull, 'w+')
console_handle = sys.stdout
sys.stdout = f

resourceValues = [0.8, 0.8, 0.8, 0.8, 0.8]

if __name__ == '__main__':

    # Create communicating pipe and sync mechanism
    write_pipe, read_pipe = Pipe()
    lock = Lock()
    sender = Process(target=init_sender, args=(read_pipe,'catane2'))
    sender.start()

    min = 0.7
    max = 1.3
    step = 0.1

    cur = min

    ### RUN GAMES WITH INCREMENTAL VALUES

    while(cur <= max):
        proc = Process(target=runner, args=(resourceValues, 0, cur, 0.7, 1.0, 0.1, lock, write_pipe,))
        proc.start()
    
        cur += step

    cur = min
    while(cur <= max):
        proc = Process(target=runner, args=(resourceValues, 0, cur, 1.1, 1.3, 0.1, lock, write_pipe,))
        proc.start()

        cur += step

    ### RUN TOP 100 CONFIGS
    # configs = get_top_100()
    #
    # n = len(configs)/8
    # for i in xrange(0, len(configs), n):
    #     proc = Process(target=config_runner, args=(configs[i:i+n], lock, write_pipe,))
    #     proc.start()


    raw_input("Press Enter to quit...")
    f.close()
