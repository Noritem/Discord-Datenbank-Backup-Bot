import discord
import pymysql
import datetime
import asyncio
import os
import configparser
import schedule

# Lade die Konfigurationsdatei
config = configparser.ConfigParser()
config.read('config.ini')

# Discord Bot-Token
TOKEN = config.get('Discord', 'TOKEN')

# MySQL-Datenbank-Verbindung
MYSQL_HOST = config.get('MySQL', 'HOST')
MYSQL_USER = config.get('MySQL', 'USER')
MYSQL_PASSWORD = config.get('MySQL', 'PASSWORD')
MYSQL_DATABASE = config.get('MySQL', 'DATABASE')

# Discord-Client initialisieren
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)

# Channel-ID für das Hochladen des Backups
CHANNEL_ID = int(config.get('Discord', 'CHANNEL_ID'))

# Option zum Löschen der Backup-Dateien vom Computer nach dem Hochladen
DELETE_BACKUP_FILES = config.getboolean('Backup', 'DELETE_FILES')

# Backup-Frequenz in Minuten
BACKUP_FREQUENCY_MINUTES = int(config.get('Backup', 'BACKUP_FREQUENCY_MINUTES'))

# Funktion zum Erstellen des Backups
async def create_backup():
    # Verbindung zur MySQL-Datenbank herstellen
    db = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    cursor = db.cursor()

    # Backup-Datei erstellen
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f'backup_{current_datetime}.sql'

    with open(backup_filename, 'w') as backup_file:
        # Tabellenstruktur abrufen
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SHOW CREATE TABLE {table_name}")
            create_table_query = cursor.fetchone()[1]
            backup_file.write(f"{create_table_query};\n\n")

            # Datensätze abrufen
            cursor.execute(f"SELECT * FROM {table_name}")
            table_data = cursor.fetchall()
            for row in table_data:
                values = [str(value) for value in row]
                insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(values)})"
                backup_file.write(f"{insert_query};\n")
            backup_file.write("\n")

    # MySQL-Datenbank-Verbindung schließen
    cursor.close()
    db.close()

    # Backup-Datei als Nachricht senden
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"Hier ist dein Backup vom {current_datetime}:", file=discord.File(backup_filename))

    # Option zum Löschen der Backup-Dateien aktiviert
    if DELETE_BACKUP_FILES:
        os.remove(backup_filename)

# Funktion zum Planen der Backup-Aufgabe
async def schedule_backup():
    while True:
        await create_backup()
        await asyncio.sleep(BACKUP_FREQUENCY_MINUTES * 60)

# Bot bereit-Event
@client.event
async def on_ready():
    print("Der Bot ist bereit.")
    client.loop.create_task(schedule_backup())

# Discord-Bot starten
client.run(TOKEN)
