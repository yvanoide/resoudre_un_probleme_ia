import pandas as pd
import mysql.connector

# Lecture du fichier CSV
file_path = '/home/yves/iadev-python/c21/Sleep_health_and_lifestyle_dataset.csv'
data = pd.read_csv(file_path)

# Connexion à la base de données MySQL
connection = mysql.connector.connect(
    host='localhost',
    user='traducteur',
    password='traducteur',
    database='health_table'
)
cursor = connection.cursor()

# Insertion des données
for index, row in data.iterrows():
    try:
        # Conversion des colonnes nécessaires
        qualite_sommeil = float(row['Quality of Sleep'])  # Assurez-vous que cela correspond au type de votre table
        rythme_cardiaque = float(row['Heart Rate'])
        etapes_quotidiennes = float(row['Daily Steps'])
        duree_sommeil = float(row['Sleep Duration'])
        score_sante = float(row['Quality of Sleep']) / 10  # Exemple d'ajustement selon votre logique

        # Requête d'insertion
        insert_query = '''
        INSERT INTO health_table (qualite_sommeil, rythme_cardiaque, etapes_quotidiennes, duree_sommeil, score_sante)
        VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (qualite_sommeil, rythme_cardiaque, etapes_quotidiennes, duree_sommeil, score_sante))
    except Exception as e:
        print(f"Erreur lors de l'insertion de la ligne {index + 1}: {e}")

# Commit des changements et fermeture de la connexion
connection.commit()
cursor.close()
connection.close()

print("Données insérées avec succès.")
