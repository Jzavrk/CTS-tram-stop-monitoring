# CTS-tram-stop-monitoring

Affichage des horaires à venir de tram en transit d'une station donnée au moyen
d'un raspberry pi.

## Dépendances

 * python3-requests
 * python3-smbus
 * i2c-tools (optionnel)

## Prérequis

 * Un écran LCD rattaché à un module I2C.

![exemple d'écran](lcd_i2c.jpg)

 * Un raspberry pi
 * Un token d'identification demandé auprés de la
   [CTS](https://api.cts-strasbourg.eu/index.html)
 * Connexion internet, cables, éléctricité, …

## Usage

Ecran connecté aux pins I2C apropriés, activez le module kernel I2C à l'aide
de `raspi-config`. 
Il faudra connaitre le numéro de bus et l'adresse du module I2C.
Le numéro de bus pour le Raspberry Pi 1 est 0, 1 pour les autres.
Pour connaitre l'adresse du module, utilisez la commande `i2cdetect -y 1` où
1 represente le numéro de bus.
La reférence de la station est consultable depuis l'API de la CTS.

Exemple d'utilisation:

	./main.py -i 0x3f --station 275A QWxhZGRpbjpvcGVuIHNlc2FtZQo= &

Un fichier de log est créé (par défaut main.py.log) pour informer des 
éventuelles problèmes.
Le script s'arrête proprement à la reception du signal SIGINT, SIGTERM ou
SIGHUP.
Pour faire démarrer le script au démarrage du rpi, utilisez cron.

Programme testé sur Raspberry Pi 3 Model B.
