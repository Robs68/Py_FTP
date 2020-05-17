#!/usr/local/bin python
# coding=utf-8

import datetime
import os
import time
import pysftp
from tqdm import tqdm

print("Lancement du script FTP\n")
start_exe = time.time()
file_list = []

localpath = ""
remotepath = ""
remoteracine = ""

IP = ''
login = ''
pathKey = ''
keypassKey = ''


class TqdmWrap(tqdm):
    def viewBar(self, a, b):
        self.total = int(b)
        self.update(int(a - self.n))  # update pbar with increment


def debit(start):
    print("")
    size = (sftp.stat(remotepath)).st_size
    print('Taille du fichier : ', size / 1e6, "mo")
    end = time.time()
    time_lapsed = end - start
    time_lapsed = datetime.timedelta(seconds=time_lapsed)
    print("temps écoulé :", time_lapsed, "secondes")
    debit = round(size / (end - start) / 1e6, 2)
    print("Le débit moyen est de : ", debit, " Mo/s")


def store_files_name(fname):
    file_names.append(fname)


def store_dir_name(dirname):
    dir_names.append(dirname)


def store_other_file_types(name):
    un_name.append(name)


def del_file():
    var = []
    command = ('cd ' + remoteracine + ' && ls -l')
    var = sftp.execute(command)
    numb = sftp.execute('cd ' + remoteracine + ' && ls -lt | wc -l')
    for i in range(1, int(numb[0])):
        file = var[i].split()
        fichier = file[8].decode('UTF-8')
        day = file[6].decode("utf-8")
        if len(day) != 2:
            day = '0' + day
        date = (day + "/" + (file[5]).decode("utf-8") + "/" + '2020' + " " + (file[7]).decode("utf-8"))
        date_object = datetime.datetime.strptime(date, '%d/%b/%Y %H:%M')
        date_actuelle = datetime.datetime.now()
        delta = date_actuelle - date_object
        fichier_suppr = remoteracine + fichier
        print(fichier_suppr)
        if delta.days >= 1:
            try:
                sftp.remove(fichier_suppr)
                print("Fichier supprimé : ", fichier)
                print("")
            except FileNotFoundError:
                print("Fichier introuvable\n")
            except OSError:
                print("Dossier error\n")
        else:
            print("Fichier non supprimé : ", fichier)
            print("")
    repertoire()


def repertoire():
    print("")
    if len(dir_names) != 0:
        print("Les noms de répertoires : ", dir_names)
        for i in range(0, int(len(dir_names))):
            command = ('rm -rf {}'.format(dir_names[i]))
            command2 = ('cd ' + remoteracine + ' && ls -l | grep -E ^d ')
            var = sftp.execute(command2)
            try:
                file2 = var[i].split()
            except IndexError:
                print("IndexError")
            day = file2[6].decode("utf-8")
            date = (day + "/" + (file2[5]).decode("utf-8") + "/" + '2020' + " " + (file2[7]).decode("utf-8"))
            date_object = datetime.datetime.strptime(date, '%d/%b/%Y %H:%M')
            date_actuelle = datetime.datetime.now()
            delta = date_actuelle - date_object
            file = dir_names[i].rsplit("/", 1)[-1]
            if delta.days >= 1:
                try:
                    sftp.execute(command)
                    print("Dossier supprimé : ", file)
                    print("")
                except FileNotFoundError:
                    print("Dossier introuvable")
                    print("")
            else:
                print("Dossier non supprimé : ", file)
                print("")
    else:
        print("Il n'y a pas de repertoire à supprimer\n")


def rename(a):
    fich2 = a.replace(' ', '.')
    sftp.rename(remotepath, fich2)


def renommage(i):
    remotepath = file_names[i]
    file = remotepath.rsplit("/", 1)[-1]
    file = file.replace('.', ' ')
    return file


print("Tentative de connexion ... ", end=" ")

sftp = pysftp.Connection(IP, username=login, private_key=pathKey,
                         private_key_pass=keypassKey)
print("Ok")
print("")

sftp.pwd
sftp.chdir('torrents/XXX')
remotedir = sftp.pwd
file_list = sftp.listdir()

file_names = []
dir_names = []
un_name = []

sftp.walktree(remotepath, store_files_name, store_dir_name, store_other_file_types, recurse=True)

print("Noms des fichiers : ")
i = 0
for file in file_names:
    file = renommage(i)
    print(file)
    i = i + 1
print("")

for i in range(0, int(len(file_names))):
    remotepath = []
    file = []
    remotepath = file_names[i]
    file = remotepath.rsplit("/", 1)[-1]
    print("Téléchargement de : ", file)
    localpath2 = os.path.join(localpath, file)
    start = time.time()
    with TqdmWrap(unit='b', unit_scale=True) as pbar:
        sftp.get(remotepath, localpath2, callback=pbar.viewBar)
    debit(start)
    try:
        rename(remotepath)
    except:
        print("Nom du fichier : ", remotepath, " non modifié\n")

del_file()

sftp.close()
stop = time.time()
delay = str(datetime.timedelta(seconds=(round(stop - start_exe, 3))))
print("Tous les éléments ont été téléchargés")
print("Temps d'exe : ", delay, " secondes")
