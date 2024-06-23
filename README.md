# Exalt - Flight radar : Gaoussou

## Table des matières
1. [À propos](#à-propos)
2. [Structure du Projet](#structure-du-projet)
3. [Installation](#installation)
4. [Utilisation](#utilisation)

## À propos

Ce projet est une bibliothèque Python conçue pour permettre l'extraction et le traitement des données de l'API flightradar24 dans le but de fournir certains indicateurs sur les vols en cours.
Elle comprend plusieurs modules et outils depuis la création des structures nécessaires, l'extraction et l'upload des données jusqu'au calcul des indicateurs.


## Structure du Projet
Ce projet est constitué d'une librairie python **lib** et d'un backend flask **backend**.

La librairie **lib** contient les différents modules pythons pour les opérations liées à la base de données (la collecte et la validation des données), le calcul des indicateurs, la gestion des jobs afin d'automatiser les opérations et quelques modules et fonctions utilitaires.  

Quant au backend flask, il a pour but de lancer les jobs permettant de lancer la collecte de données et le calcul d'indicateur en spécifiant une fréquence d'exécution pour chaque tâche, mais aussi de les arrêter. il permet également de récuperer les résultats des indicateurs calculés.

J'ai fait le choix de lancer à la fois la collecte de données en continue, mais également le calcul des indicateurs dans le but d'avoir une historique pour chaque indicateur. 

Les données flight sont donc stockés avec un champ **latest_update** qui permet donc de déterminer la dernière mise à jour pour un vol donné.


Pour les indicateurs, le champ **computation_timestamp** spécifie quand est-ce qu'un indicateur donné a été calculé.

Un utilisateur peut donc décider de demander le résultat d'un indicateur en temps réel ou bien une historique de ceci, ce qui pourra lui permettre de faire une comparaison dans le temps et de voir comment cet indicateur évolue.

### 1. Lib
```plaintext
lib
 ├── db_toolkits
 │   ├── exalt_handler
 │   │   ├── __init__.py
 │   │   ├── add.py
 │   │   ├── create.py
 │   │   └── get.py
 │   ├── utilities
 │   │   ├── __init__.py
 │   │   ├── processing_functions.py
 │   │   └── table_mappings.py
 │   └── __init__.py
 ├── data_upload
 │   ├── __init__.py
 │   ├── data_validation.py
 │   └── flight_data.py
 ├── indicators
 │   ├── __init__.py
 │   └── processor.py
 ├── utilities
 │   ├── __init__.py
 │   ├── exceptions.py
 │   ├── job_execution.py
 │   └── job_handler.py
 │   └── log_handler.py
 ├── __init__.py
 └── setup.py
 ```

#### 1.1 Db_toolkits
Il contient des outils pour la gestion de la base de données. Il permet la création des tables **flight** et **indicator**, l'ajout des données, mais également la récupération des données.
Si demain le projet évolue et que l'on a besoin d'une nouvelle table, il suffit d'ajouter son mapping et la table sera automatiquement créée.
  - **exalt_handler** : Gestion des opérations liées de la base de données.
    - `add.py` : Ajout de données.
    - `create.py` : Création de structures.
    - `get.py` : Récupération de données.
  - **utilities** : Fonctions utilitaires pour la manipulation des données.
    - `processing_functions.py` : Fonctions de traitement.
    - `table_mappings.py` : Mappings des tables.

#### 1.2 Data_upload
Il contient les modules responsables de l'extraction des données de l'API FlightRadar24, de leur validation et de leur insertion dans la base de données.

Le module **FlightDataUploader** s'occupe de récupérer les données de vol à travers la lib python *flightradar24*  et de les traiter pour qu'elle soit sous le format attendu par la base de données.

Le module **DataValidator** qui est responsable de la validation des données de vol. La validation est effectuée en utilisant le schéma généré dynamiquement basé sur le mapping de la base de données et les règles d'intégrité définies. 

Les règles d'intégrité sont définies dans le *__init__.py'. J'ai fait le choix de ne faire valider que certaines données qui interviennent dans le calcul des différents indicateurs tels que le nom de la companie aérienne, l'aéroport d'origine et de destination etc.

Les champs présents dans la règle doivent être vérifiés avant insertion. C'est-à-dire pour qu'ils soient valides, il faut que leurs types correspondent à ceux définis dans la base de données et également elles ne doivent pas être manquantes. 
Pour ces champs on définit des status qui sont insérés avec les données et qui spécifient si le champ était valide, manquant ou invalide.

On peut aussi faire plus et demander de vérifier l'intervalle ou les valeurs possibles pour chaque donnée.

Lors des calculs des indicateurs, on pourra donc spécifier de ne prendre en compte que les données valides ou bien de considérer toutes les données.
Ce choix me permet de conserver toutes les données, et de pouvoir filtrer lors de l'usage.

#### 1.3 Indicators 
Ce package contient les modules nécessaires pour le calcul des indicateurs basés sur les données de vols en temps réel et leur stockage dans la base de données.
Contenu des fichiers
- **__init__.py** : définit la liste des indicateurs à calculer :
    - `airline_with_most_live_flights`
    - `airline_with_most_regional_flights_per_continent`
    - `longest_ongoing_flight`
    - `average_flight_length_per_continent`
    - `manufacturer_with_most_active_flights`
    - `top_aircraft_models_per_airline`
    - `airport_with_largest_flights_difference`
- **processor.py** : contient la classe IndicatorProcessor qui calcule les indicateurs définis. 
La classe utilise des requêtes SQL pour extraire et analyser les données à partir de la base de données.
Voici les principales méthodes de la classe IndicatorProcessor:

`__init__` : Initialise la connexion à la base de données, crée un curseur et vérifie si des données de vol sont disponibles pour le calcul des indicateurs.

`get_airline_with_most_live_flights` : Calcule et renvoie la compagnie aérienne avec le plus grand nombre de vols en cours.

`get_airline_with_most_regional_flights_per_continent` : Calcule et renvoie la compagnie aérienne avec le plus grand nombre de vols régionaux pour chaque continent.

`get_longest_ongoing_flight` : Calcule et renvoie le vol en cours le plus long basé sur la distance entre l'aéroport d'origine et de destination.

`get_average_flight_length_per_continent` : Calcule et renvoie la longueur moyenne des vols pour chaque continent.

`get_manufacturer_with_most_active_flights` : Calcule et renvoie le constructeur d'avions avec le plus grand nombre de vols actifs.

`get_top_aircraft_models_per_airline` : Calcule et renvoie les modèles d'avions les plus utilisés pour chaque compagnie aérienne, avec un nombre limité de modèles les plus fréquents.

`get_airport_with_largest_flights_difference` : Calcule et renvoie l'aéroport avec la plus grande différence entre les vols au départ et à l'arrivée.

`process` : Est la méthode principale. Elle exécute le calcul pour tous les indicateurs définis dans INDICATORS et stocke les résultats dans la base de données.

#### 1.4 Utilities
Ce package contient des fichiers utilitaires essentiels pour la gestion des exceptions, la planification et l'exécution des tâches et la gestion des logs.

Voici une description détaillée de chaque fichier :

`exceptions.py`: définit les classes d'exceptions personnalisées pour gérer différentes erreurs.

`job_handler.py`: contient la classe JobHandler qui gère la planification et l'exécution des tâches en utilisant APScheduler avec un stockage des tâches dans une base de données PostgreSQL.

`job_executor.py`: contient la fonction job_executor qui exécute les tâches en fonction du type de tâche. 
Cette fonction exécute soit le processus de téléchargement des données de vol via FlightDataUploader, soit le calcul des indicateurs via IndicatorProcessor. 
Si le type de tâche est inconnu, elle retourne une erreur.

`log_handler.py`: contient la fonction qui gère l'écriture des logs.

Le package **lib** est la composante la plus importante et constitue une lib pouvant être installé dans les backends. 

**Lib** a donc les fonctionnalités nécessaires pour la collecte des données de vol, leur traitement et puis le calcul des indicateurs demandés. 
Elle contient également les modules pour pouvoir lancer des jobs en continue.
 
### 2. Backend
```plaintext
backend
│
├── app
│   ├── endpoints
│   │   ├── __init__.py
│   │   ├── indicators.py
│   │   ├── jobs.py
│   │   └── utilities.py
│   ├── __init__.py
└── __init__.py
```
Ce backend flask est dedié à l'administration des tâches, le lancement et l'arrêt des modules pour la collecte des données et le calcul continu des indicateurs.

Les différents endpoints pour interagir avec les fonctionnalités de l'application sont définis dans le dossier endpoints.

`jobs.py`: contient les endpoints suivants

- `Endpoint /start (POST)` : Il démarre les jobs d'upload de données de vol et de calcul d'indicateurs. Il s'assure qu'aucun job n'est en cours pour ne pas lancer plusieurs fois ces jobs.
- `Endpoint /stop (PUT)` : Il  arrête tous les jobs d'upload de données de vol et de calcul d'indicateurs planifiés.
- `Endpoint /jobs (GET)` : Il récupère tous les jobs planifiés et renvoie une liste JSON des jobs planifiés ou un message d'erreur en cas de problème.

`indicators.py`:  
Il contient l'endpoint `/indicators/<string:indicator>` qui permet de récupérer les résultats des indicateurs calculés dans la base de données. 

Ce dernier prend en paramètre un nom d'indicateur (indicateur_1, indicateur_2), vérifie s'il existe et récupère la dernière valeur computée pour cet indicateur.

## Installation
Pour installer et configurer l'appli, suivez les étapes ci-dessous :
1. **Clonage du Répertoire**
```plaintext
git clone <project_url>
cd flight_radar
```
2. **Environnement Virtuel** (optionnel mais recommandé)
```plaintext
python -m venv env
source env/bin/activate  # Pour Linux/macOS
env\Scripts\activate  # Pour Windows
```
3. **Installation des Dépendances**

il faut installer lib qui va installer toutes les dépendances Python nécessaires.
```plaintext
pip install -e lib/
```
4. **Configuration de la Base de Données**

Les crédentials d'accès à une base de données Postgresql doivent être mis dans la variable ADMIN_CREDENTIAL dans le fichier ```lib/db_toolkits/exalt_handler/__init__.py```.
```plaintext
 ADMIN_CREDENTIAL = {
     "name": "exalt_fr_db",
     "host": "localhost",
     "user": "my_exalt_user",
     "password": "myExaltPwd",
     "port": 5432
}
```
5. **Démarrage du Serveur**
```plaintext
 cd backend
 python -m flask run
```
6. **Usage**

Une fois le backend lancé, vous pouvez utiliser un outil comme Postman pour accéder aux endpoints définis dans l'application backend.
J'ai aussi réalisé une interface graphique simple avec streamlit pour faciliter l'usage.

Les deux usages sont décrits dans la section [Utilisation](#utilisation).

## Utilisation
Il faut tout d'abord lancer le backend flask en suivant les étapes dans [Installation](#installation).

Une fois le backend lancé, vous pouvez soit utiliser des outils comme Postman (ci dessous une collection postman avec les différents endpoints), 
ou bien utiliser l'interface graphique streamlit.
1. **Postman**
```json
{
	"info": {
		"_postman_id": "ac557fb5-00f7-4bf2-8ef5-f7b88f974973",
		"name": "Exalt-fr",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
		"_exporter_id": "36455659"
	},
	"item": [
		{
			"name": "start",
			"request": {
				"method": "PUT",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \n}",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "{{exalt_flight_radar}}/start",
					"host": [
						"{{exalt_flight_radar}}"
					],
					"path": [
						"start"
					]
				}
			},
			"response": []
		},
		{
			"name": "stop",
			"request": {
				"method": "PUT",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \n}",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "{{exalt_flight_radar}}/start",
					"host": [
						"{{exalt_flight_radar}}"
					],
					"path": [
						"start"
					]
				}
			},
			"response": []
		},
		{
			"name": "jobs",
			"protocolProfileBehavior": {
				"disableBodyPruning": true
			},
			"request": {
				"method": "GET",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \n}",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "{{exalt_flight_radar}}/jobs",
					"host": [
						"{{exalt_flight_radar}}"
					],
					"path": [
						"jobs"
					]
				}
			},
			"response": []
		},
		{
			"name": "indicators",
			"protocolProfileBehavior": {
				"disableBodyPruning": true
			},
			"request": {
				"method": "GET",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": "{\n    \n}",
					"options": {
						"raw": {
							"language": "json"
						}
					}
				},
				"url": {
					"raw": "{{exalt_flight_radar}}/indicators/indicator_2",
					"host": [
						"{{exalt_flight_radar}}"
					],
					"path": [
						"indicators",
						"indicator_2"
					]
				}
			},
			"response": []
		}
	],
	"event": [
		{
			"listen": "prerequest",
			"script": {
				"type": "text/javascript",
				"packages": {},
				"exec": [
					""
				]
			}
		},
		{
			"listen": "test",
			"script": {
				"type": "text/javascript",
				"packages": {},
				"exec": [
					""
				]
			}
		}
	],
	"variable": [
		{
			"key": "exalt_flight_radar",
			"value": "http://127.0.0.1:5000",
			"type": "string"
		}
	]
}
```

2. **Interface graphique**
Pour démarrer l'interface graphique, il faut depuis la racine du projet:
```plaintext
 cd frontend
 streamlit run app.py
```
Dans le menu à gauche, il y a la fenêtre administration où il est possible de planifier les jobs en donnant une date de début et les fréquences d'exécution, mais également les arrêter.

Et la page principale est dédiée aux indicateurs.