#!/usr/bin/python3

import qrcode
import os
import subprocess
import sys
from PIL import Image
import requests, json

def vers_8bit(c):
	chaine_binaire = bin(ord(c))[2:]
	return "0"*(8-len(chaine_binaire))+chaine_binaire

def modifier_pixel(pixel, bit):
	# on modifie que la composante rouge
	r_val = pixel[0]
	rep_binaire = bin(r_val)[2:]
	rep_bin_mod = rep_binaire[:-1] + bit
	r_val = int(rep_bin_mod, 2)
	return tuple([r_val] + list(pixel[1:]))

def recuperer_bit_pfaible(pixel):
	r_val = pixel[0]
	return bin(r_val)[-1]

def cacher(image,message):
	dimX,dimY = image.size
	im = image.load()
	message_binaire = ''.join([vers_8bit(c) for c in message])
	posx_pixel = 0
	posy_pixel = 0
	for bit in message_binaire:
		im[posx_pixel,posy_pixel] = modifier_pixel(im[posx_pixel,posy_pixel],bit)
		posx_pixel += 1
		if (posx_pixel == dimX):
			posx_pixel = 0
			posy_pixel += 1
		assert(posy_pixel < dimY)

def recuperer(image,taille):
	message = ""
	dimX,dimY = image.size
	im = image.load()
	posx_pixel = 0
	posy_pixel = 0
	for rang_car in range(0,taille):
		rep_binaire = ""
		for rang_bit in range(0,8):
			rep_binaire += recuperer_bit_pfaible(im[posx_pixel,posy_pixel])
			posx_pixel +=1
			if (posx_pixel == dimX):
				posx_pixel = 0
				posy_pixel += 1
		message += chr(int(rep_binaire, 2))
	return message

def cachemes(identite,intitule_certif):
	m=identite+"/"+intitule_certif
	m=m.zfill(64)

	try:
		f = open("file.tsr","rb")
	except Exception as e:
		print(e.args)
		sys.exit(1)

	d=b""
	while(1):
		ligne=f.read(1)
		d=d+ligne
		if not ligne:
			break
	
	d=str(d)
	messageacacher=m+d
	f.close()
	nom_fichier = ("attestation.png")
	message_a_traiter = messageacacher
	print ("Longueur message : ",len(message_a_traiter))
	mon_image = Image.open(nom_fichier)
	cacher(mon_image, message_a_traiter)
	mon_image.save('stegano_'+nom_fichier)


def créa_attestation(identite, intitule_certif):
	try:
		CarteCrypto = open("CarteCrypto.txt","a")
	except Exception as e:
		print(e.args)
		sys.exit(1)

	CarteCrypto.write(identite+"\n")
	CarteCrypto.write(intitule_certif+"\n")
	CarteCrypto.close()


	commande4 = subprocess.Popen("openssl dgst -sha256 -sign ecc.ca.key.pem CarteCrypto.txt > sig.txt", shell=True, stdout=subprocess.PIPE)
	(sig, ignorer4) = commande4.communicate()

	commande5 = subprocess.Popen("openssl base64 -A -in sig.txt -out signature.txt", shell = True, stdout=subprocess.PIPE)
	(signature, ignorer5) = commande5.communicate()

	#creation du code QR
	try:
		g = open("qrcode.png","a")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	g.close()
	try:
		f = open("signature.txt","r")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	data=""
	while(1):
		ligne=f.read(1)
		data=data+ligne
		if not ligne:
			break
	f.close()
	nom_fichier = "qrcode.png"
	qr = qrcode.make(data)
	qr.save(nom_fichier, scale=2)

	#Ajout du nom, prénom et formation à l'attestation
	#Passage par l'outil google chart pour créer texte.png

	texte=("Attestation de réussite en {}|délivrée à {}").format(intitule_certif,identite)

	url="http://chart.apis.google.com/chart"

	headers = {
	    'Content-type': 'application/json',
	}
	params = {
	"chst":"d_text_outline",
	"chld":"000000|56|h|FFFFFF|b|{}".format(texte)
	}
	response = requests.get(url, headers=headers, params=params)
	file = open("texte.png", "ab")
	file.write(response.content)
	file.close()

	#Ajout de texte.png et qrcode.png au fond de  l'attestation après avoir modifié leurs formats
	commande1 = subprocess.Popen("mogrify -resize 1000x600 texte.png", shell = True, stdout=subprocess.PIPE)
	(test1, ignorer1) = commande1.communicate()

	commande2 = subprocess.Popen("composite -gravity center texte.png fond_attestation.png combinaison.png", shell = True, stdout=subprocess.PIPE)
	(test2, ignorer2) = commande2.communicate()

	commande3 = subprocess.Popen("mogrify -resize 200x200 qrcode.png", shell = True, stdout=subprocess.PIPE)
	(test3, ignorer3) = commande3.communicate()

	commande4 = subprocess.Popen("composite -geometry +1418+934 qrcode.png combinaison.png attestation.png", shell = True, stdout=subprocess.PIPE)
	(test4, ignorer4) = commande4.communicate()

	#Calcul du timestamp
	commande1 = subprocess.Popen("openssl ts -query -data attestation.png -no_nonce -sha512 -cert -out file.tsq", shell = True, stdout=subprocess.PIPE)
	(test1, ignorer1) = commande1.communicate()

	commande2 = subprocess.Popen("curl -H 'Content-Type: application/timestamp-query' --data-binary '@file.tsq' https://freetsa.org/tsr", shell = True, stdout=subprocess.PIPE)
	(timestamp, ignorer2) = commande2.communicate()

	try:
		f = open("file.tsr","ab")
	except Exception as e:
		print(e.args)
		sys.exit(1)

	f.write(timestamp)
	f.close()

	#Ajout du timestamp et informations à l'attestation par stenographie
	cachemes(identite,intitule_certif)

	return "ok!"

