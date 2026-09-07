"""
Rende importabile il pacchetto `app` durante i test.

pytest, in modalità di import «prepend», inserisce in `sys.path` la cartella che
contiene il `conftest.py` più esterno. La sola presenza di questo file basta
quindi a far funzionare `from app.core.config import ...` da qualunque cartella
si lanci la suite, senza installare il progetto né manipolare `sys.path` a mano.
"""
