import subprocess
import sys

def install_dependencies():
    dependencies = [
        'discord.py',
        'pymysql',
        'schedule'
    ]

    for dependency in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dependency])
            print(f"{dependency} wurde erfolgreich installiert.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Installieren von {dependency}: {str(e)}")

if __name__ == '__main__':
    print("Installiere Abhängigkeiten...")
    install_dependencies()
    print("Installation abgeschlossen.")
