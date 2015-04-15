#!/usr/bin/python
#-*- coding: latin-1 -*-

# Joueur du jeu de Catane
#
# Date: 29 février 2012
#
# Auteur: Michel Gagnon



import sys
import getopt
import random

from Joueur import *
from JoueurAI import *
from JoueurHumain import *


class FabriqueJoueur:
    def __init__(self):
        pass

    def creerJoueur(self,nomJoueur,id):
        if nomJoueur == 'AI':
            return JoueurAI(id)
        elif nomJoueur == 'Humain':
            return JoueurHumain(id)
        else:
            raise RuntimeError("Création de joueur: Numéro invalide")
