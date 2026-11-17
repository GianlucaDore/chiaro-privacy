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

#   Decisione:
#     Nei test il motore dell'app usa un database in memoria, e non quello di sviluppo.
#     I test lavorano sul test.db della fixture `engine`: questo database è solo una rete di
#     sicurezza. Una richiesta che sfugge all'override di get_db fallisce subito, perché trova
#     un database senza tabelle, invece di scrivere in silenzio nel database di sviluppo.
#     Sta qua perché il motore lo crea app/db/session.py, con create_engine scritta fuori da
#     ogni funzione: gira una volta sola, al primo import del file, e legge DATABASE_URL in
#     quel momento. Il primo import avviene mentre pytest carica tests/conftest.py, prima di
#     ogni test; questo file viene eseguito prima ancora, e la variabile arriva in tempo.
#     Dentro una fixture sarebbe troppo tardi: il motore esisterebbe già.
#     È un'assegnazione, non `os.environ.setdefault(...)`: un DATABASE_URL già presente
#     nella shell o nel .env vincerebbe, e potrebbe essere proprio quello di sviluppo.
os.environ["DATABASE_URL"] = "sqlite://"
