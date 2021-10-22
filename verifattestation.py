#!/usr/bin/python3

import qrcode
import subprocess
import sys
from PIL import Image
import zbarlight

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


#il est écrit dans le sujet que l'estmpille a une taille fixe
#et nom,prénom et formation est sur 64 caractéres

def recupmes(nom_fichier):
	saisie = 15000
	message_a_traiter = int(saisie)
	mon_image = Image.open(nom_fichier)
	message_retrouve = recuperer(mon_image, message_a_traiter)
	#print (message_retrouve)
	return message_retrouve

def verifattes(nom_fichier):
	#récuperation des informations qu'on va ensuite vérifier
	x=recupmes(nom_fichier)
	infosrec=x[:64]
	p=x[64:]

	try:
		f = open("timestampaverif.txt","a")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	print('\n')
	f.write(p)
	f.close()


	#vérification du timestamp auprès de l'authorité
	try:
		f1 = open("timestampaverif.txt","r")
	except Exception as e:
		print(e.args)
		sys.exit(1)

	try:
		f2 = open("file.tsr","rb")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	d1=""
	d2=b""
	while(1):
		c1=f1.read(1)
		d1=d1+c1
		if not c1:
			break

	while(1):
		c2=f2.read(1)
		d2=d2+c2
		if not c2:
			break
	f1.close()
	f2.close()
	
	d1=str(d1)
	d2=str(d2)
	v=len(d2)
	d1=d1[:v]
	if(d1==d2):
		m = subprocess.run("openssl ts -verify -in file.tsr -queryfile file.tsq -CAfile cacert.pem -untrusted tsa.crt", shell = True)
		verif=m.returncode
		if(verif==0):
			print('timestamp ok')
			res_ts=True
		else:
			print('timestamp not ok')
			res_ts=False
	else:
		res_ts=False


	#vérification des infos
	infos=[]
	for i in infosrec:
		if(i!='0'):
			infos.append(i)
	infos=('').join(infos)
	j=infos.find('/')
	identite=infos[:j]
	formation=infos[j+1:]
	try:
		inf = open("infosaverif.txt","a")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	inf.write(identite+"\n")
	inf.write(formation+"\n")
	inf.close()


	#pour récuperer le code qr
	attestation = Image.open('stegano_attestation.png')
	qrImage = attestation.crop((1418,934,1418+210,934+210))
	qrImage.save("qrcoderecupere.png", "PNG")

	#pour récuperer les infos dans le code qr
	image = Image.open("qrcoderecupere.png")
	data = zbarlight.scan_codes(['qrcode'], image)
	data=str(data)
	data="".join(data)
	n=len(data)
	x=data[3:n-2]
	try:
		f= open("sigaverif.txt","a")
	except Exception as e:
		print(e.args)
		sys.exit(1)
	f.write(x)
	f.close()

	subprocess.run("openssl enc -base64 -d -A -in sigaverif.txt >signatureaverif.txt", shell=True)

	res = subprocess.run("openssl dgst -verify ecc.pubkey.serveur_applicatif.pem -signature signatureaverif.txt infosaverif.txt", shell=True)
	if (res.returncode == 0):
	    print('sig ok')
	    res_sig=True
	else:
	    print('sig not ok')
	    res_sig=False

	if res_ts==True and res_sig==True:
		resverif=True
	else:
		resverif=False

	return resverif





