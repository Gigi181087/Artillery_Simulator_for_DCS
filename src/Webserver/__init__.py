import sys
import os

# Setze den Pfad relativ zum aktuellen Dateistandort
package_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(package_dir, '..'))

# Überprüfe, ob der Pfad schon in sys.path ist
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Hier könntest du weitere Initialisierungen vornehmen, falls nötig
