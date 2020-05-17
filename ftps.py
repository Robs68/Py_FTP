#!/usr/local/bin python
# coding=utf-8

import datetime
import ftplib
import os
import sys
import time
from ftplib import FTP_TLS

import ftputil
from tqdm import tqdm

print("Lancement du script FTP\n")
start_exe = time.time()

server = ''
user = ''
password = ''
dest_dir = ''

try:
    if sys.argv[1] in 'films':
        print('Téléchargement de films')
        remotepath = "/files/Robin_films/"
    elif sys.argv[1] in 'séries':
        print('Téléchargement de Séries')
        remotepath = "/files/Robin_series/"
    elif sys.argv[1] in 'soft':
        print('Téléchargement de Logiciels')
        remotepath = "/files/Robin_Soft/"
    else:
        raise ValueError("Mauvais arguments")
except:
    raise ValueError("Pas d'argments")

print("Lancement de la connexion ...", end='')
ftps = FTP_TLS(server)
ftps.login(user=user, passwd=password)
ftp = ftputil.FTPHost(server, user, password, session_factory=ftplib.FTP_TLS)
print(' ok\n')

ftps.cwd(remotepath)
ftps.dir()


def renomage(chemin):
    file_list = []
    ftps.retrlines('NLST', lambda x: file_list.append(x.split()))
    for file in range(len(file_list)):
        if len(file_list[file]) > 1:
            print("Renomage de :", file_list[file])
            fichier_rename = ' '.join(file_list[file][0:])
            fichier = '.'.join(file_list[file])
            ftps.rename(chemin + fichier_rename, chemin + fichier)


def del_file():
    repertoire = (ftp.listdir(remotepath))
    for f in range(len(repertoire)):
        heure_files = int((ftp.stat((ftp.path.join(remotepath + repertoire[f]))))[8])
        yesterday = (datetime.datetime.now() - datetime.timedelta(2))
        yesterday = yesterday.timestamp()
        if heure_files < yesterday:
            if ((ftp.stat((ftp.path.join('/files/Robin_Soft/'+ repertoire[f]))))[0]) is '16877':
                print("Fichier supprimé : ", repertoire[f], " ", end= "")
            else :
                ftp.rmtree(remotepath + repertoire[f], ignore_errors=True)
            print(" Ok")
    print("Il n'y a pas de fichiers à supprimer : trop récent")


def renomage_v2():
    file_list = []
    ftps.retrlines('LIST', lambda x: file_list.append(x.split()))
    for i in range(len(file_list)):
        if file_list[i][0] == '-rw-rw-rw-':
            renomage(remotepath)
        else:
            files_d = ftps.nlst()
            path = remotepath + (file_list[i][8]) + '/'
            try :
                ftps.cwd(path)
            except:
                pass
            for f in range(len(files_d)):
                renomage(path)


renomage_v2()

os.chdir(dest_dir)

fichiers = []
for item in ftp.walk(remotepath, topdown=True):
    longeur = len(remotepath)
    try :
        os.mkdir(item[0][longeur:])
    except:
        pass
    for files in item[2]:
        total = ftp.path.getsize(ftp.path.join(item[0],files))
        with tqdm(unit='b', unit_scale=True, leave=False, miniters=1, desc='Téléchargement de : {} '.format(files), total=total) as tqdm_instance:
            ftp.download(ftp.path.join(item[0],files), os.path.join(item[0][longeur:],files), callback=lambda sent: tqdm_instance.update(len(sent)))
        fichiers.append(files)


for i in range(len(fichiers)):
    print("Les fichiers téléchargés sont : ", fichiers[i])

print("")
del_file()
ftps.quit()
stop = time.time()
delay = str(datetime.timedelta(seconds=(round(stop - start_exe, 3))))
print("Tous les éléments du dossier {} ont été téléchargés".format(remotepath))
print("Temps d'exe : ", delay, " secondes")
