# Relevé des codes de ligne Navigo

Objectif: remplir `NAVIGO_LINE_NAMES` dans `api/calypso/transit/navigo.c`. Chaque
validation écrit un `EventRouteNumber` dans la carte; il faut connaître avec
certitude la ligne empruntée pour associer le code au nom commercial.

## Méthode

1. Valider sur une ligne identifiable sans ambiguïté (voir les listes ci-dessous).
2. Scanner la carte avec Metroflip et sauvegarder le scan.
3. Décoder la sauvegarde: `python3 tools/navigo_decode.py <save.nfc>`, puis noter
   `transport`, `route` et la station de chaque event.
4. Reporter la valeur dans la colonne "code relevé" de ce fichier, et ajouter
   l'entrée dans `NAVIGO_LINE_NAMES`.

Contrainte importante: la carte ne garde que **3 events**. Il faut donc scanner
au plus tard après trois validations, sinon les plus anciennes sont écrasées.

Deux pièges à garder en tête:

- En métro et en RER, la validation a lieu à un portillon de gare, et le code
  enregistré est celui du portillon, pas de la ligne que l'on emprunte ensuite.
  D'où l'obligation de choisir une gare desservie par une seule ligne.
- En tram et en bus, la validation est à bord: le code correspond forcément à la
  ligne du véhicule, n'importe quel arrêt convient.

## Priorité 1: trancher la question du métro

Le code 13 a été relevé à Invalides, desservie par la 8 et la 13. Il faut savoir
si les codes métro sont bien les numéros commerciaux.

| Ligne | Gare mono-ligne à valider | Code attendu si identité | Code relevé |
|-------|---------------------------|--------------------------|-------------|
| 8     | Faidherbe-Chaligny ou Pointe du Lac | 8 | |
| 13    | Guy Môquet                          | 13 | |

Si la 8 renvoie 8 et la 13 renvoie 13, la numérotation métro est l'identité et
l'event d'Invalides était correct (portillon côté ligne 13). Sinon il faudra une
entrée par ligne.

## Métro

Gares desservies par une seule ligne, avec portillons.

| Ligne  | Gare mono-ligne        | Code relevé |
|--------|------------------------|-------------|
| 1      | Argentine ou Saint-Paul | |
| 2      | Anvers                 | |
| 3      | Europe                 | |
| 3 bis  | Pelleport              | |
| 4      | Vavin                  | |
| 5      | Laumière               | |
| 6      | Dupleix                | |
| 7      | Riquet                 | |
| 7 bis  | Buttes-Chaumont        | |
| 8      | Faidherbe-Chaligny     | |
| 9      | Ranelagh               | |
| 10     | Cardinal Lemoine       | |
| 11     | Pyrénées               | |
| 12     | Rue du Bac             | |
| 13     | Guy Môquet             | |
| 14     | Cour Saint-Émilion     | |

Codes déjà connus: 103 = 3 bis (et 107 = 7 bis, déduit du même décalage de 100,
à confirmer à Buttes-Chaumont).

## RER

| Ligne | Gare mono-ligne          | Code relevé |
|-------|--------------------------|-------------|
| A     | Auber                    | 17 (confirmé) |
| A     | Neuilly-Plaisance        | 26 (confirmé) |
| B     | Luxembourg ou Cité Universitaire | |
| C     | Musée d'Orsay ou Javel   | |
| D     | Créteil-Pompadour ou Maisons-Alfort-Alfortville | |
| E     | Rosa Parks ou Magenta    | |

Le RER A donne deux codes différents selon la gare, donc le code semble lié à la
section ou à la branche et pas seulement à la ligne. À échantillonner pour
comprendre la logique:

| Section / branche      | Gare mono-ligne     | Code relevé |
|------------------------|---------------------|-------------|
| Tronçon central        | Auber               | 17 |
| Est, tronçon Vincennes | Vincennes           | |
| Est, branche A4        | Torcy               | |
| Est, branche A2        | Neuilly-Plaisance   | 26 |
| Ouest, branche A1      | Le Vésinet-Centre   | |
| Ouest, branche A3      | Rueil-Malmaison     | |

## Transilien (SNCF)

Plus long à couvrir, et le transporteur diffère (`EventServiceProvider` = 2 au
lieu de 3), donc l'espace de codes est peut-être distinct. À faire à l'occasion.

| Ligne | Gare mono-ligne                  | Code relevé |
|-------|----------------------------------|-------------|
| H     | Sarcelles-Saint-Brice            | |
| J     | Argenteuil                       | |
| K     | Dammartin-Juilly-Saint-Mard      | |
| L     | Marly-le-Roi                     | |
| N     | Bellevue                         | |
| P     | Vaires-Torcy                     | |
| R     | Bois-le-Roi                      | |
| U     | (aucune gare mono-ligne, à traiter autrement) | |

## Tram

Validation à bord: un simple trajet suffit, aucune gare à choisir.

| Ligne | Code relevé |
|-------|-------------|
| T1    | |
| T2    | |
| T3a   | 1 et 13 (déjà en table) |
| T3b   | |
| T4    | |
| T5    | |
| T6    | 16 (déjà en table) |
| T7    | |
| T8    | 18 (déjà en table) |
| T9    | 9 (déjà en table) |
| T10   | |
| T11   | |
| T12   | |
| T13   | |
| T14   | |

T3a apparaît avec deux codes (1 et 13), comme le RER A: vérifier si le code
dépend du sens ou du secteur en validant dans les deux directions.

## Bus

Les numéros de bus sont supposés être les numéros commerciaux. Un contrôle sur
deux ou trois lignes suffit: valider, décoder, vérifier que le numéro affiché est
bien celui du bus emprunté. Noter aussi le `Door` et le `Side`, qui sortent du
même champ `EventDevice`.

| Ligne empruntée | Code relevé | Numéro correct ? |
|-----------------|-------------|------------------|
|                 |             |                  |
