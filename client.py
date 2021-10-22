#!/usr/bin/python3

import qrcode
import subprocess
import sys
from PIL import Image
import requests, json
from bottle import route, run, template, request, response

print("Bienvenue au service CertiPlus\n")
print("Si vous souhaitez générer une attestation tapez '1' \n")
print("si vous souhaitez vérifier une attestation tapez '2' \n")
print("si vous souhaitez recuperer une attestation tapez '3' \n")
print("vous pouvez quitter a tout moment en tapant ctrl+c \n")
choix=input()
if (choix=='1'):
	print("Vous avez choisi de générer une attestation \n")
	identite=input("veuillez donner votre nom et prénom : ")
	intitule_certif=input("veuillez donner l'intitulé de votre formation : ")
	subprocess.run("curl -v -X POST -d 'identite= "+identite+"' -d 'intitule_certif="+intitule_certif+"' --cacert \ecc.serveur_frontal.pem https://localhost:9000/creation", shell = True)
if (choix=='2'):
	print("vous avez choisi de vérifier une attestation \n")
	print("veuillez entre le nom du fichier contenant votre attestation \n")
	fichier=input()
	subprocess.run(" curl -v -F image=@"+fichier+" --cacert \ecc.serveur_frontal.pem https://localhost:9000/verification", shell = True)
if(choix=='3'):
	print("vous avez choisi de recuperer une attestation \n")
	print("votre attestation sera enregistré dans le fichier mon_image.png")
	subprocess.run("curl -v -o mon_image.png --cacert \ecc.serveur_frontal.pem https://localhost:9000/fond", shell = True)


