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

Activé le module kernel i2c avec `raspi-config`. Le bus i2c étant disponible,
son identifient est **0** pour le raspberry pi 1 et **1** pour les versions
supérieurs.  Il faudra connaitre l'adresse du module i2c en utilisant la 
commande `i2cdetect -y 1`. Enfin, la reférence de la station est consultable
directement sur l'API de la CTS.

Exemple d'utilisation:

	./main.py -i 0x3f --station 275A QWxhZGRpbjpvcGVuIHNlc2FtZQo= &

Un fichier de log est créé (par défaut main.py.log) pour informer des 
éventuelles problèmes.

Le script s'arrête proprement à la reception du signal SIGINT, SIGTERM ou
SIGHUP.

Pour faire démarrer le script au démarrage du rpi, utilisez cron.
