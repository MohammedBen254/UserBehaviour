# UserBehaviour

Exemple de donnees (Vue *UserActivitySummary*) :
<img width="1455" height="128" alt="image" src="https://github.com/user-attachments/assets/7325e39c-07e1-44e7-9db1-f063ba551377" />

La vue UserActivitySummary affiche un résumé de l'activité de chaque utilisateur sur votre site/appli, regroupant des données provenant de différentes tables. Voici ce que chaque colonne signifie :

Colonnes affichées :
user_id → Identifiant unique de l'utilisateur.

created_at → Date/heure de création du compte utilisateur.

num_visited_pages → Nombre de pages différentes visitées par l'utilisateur.

visited_urls → Liste de toutes les URLs visitées (concaténées en une seule chaîne).

num_clicks → Nombre total de clics effectués par l'utilisateur.

num_button_clicks → Sous-ensemble des clics, comptant seulement ceux sur des boutons (<button>) ou liens (<a>).

time_on_site_seconds → Temps total passé sur le site (en secondes), calculé entre le 1er et le dernier événement.

user_needs → Messages saisis par l'utilisateur (ex: feedback, demandes d'aide), regroupés en une seule chaîne.
