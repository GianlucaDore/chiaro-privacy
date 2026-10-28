"""
Rende importabile il pacchetto `app` durante i test.

pytest, in modalità di import «prepend», inserisce in `sys.path` la cartella che
contiene il `conftest.py` più esterno. La sola presenza di questo file basta
quindi a far funzionare `from app.core.config import ...` da qualunque cartella
si lanci la suite, senza installare il progetto né manipolare `sys.path` a mano.
"""

import os

#   Decisione:
#    i test devono girare identici su ogni macchina e anche in CI. Bisogna settare la variabile
#    di ambiente per i test, ma non può essere né DEV né PROD: se fosse una delle due, ci sarebbe
#    il rischio che i tests vadano a contaminare le risorse (DB, logs...) degli ambienti di DEV
#    o di PROD. Quindi settiamo come ambiente un ambiente "recluso" con risorse finte, proprio TEST.

os.environ["ENV"] = "TEST"
