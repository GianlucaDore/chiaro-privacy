"""
Rende importabile il pacchetto `app` durante i test.

pytest, in modalità di import «prepend», inserisce in `sys.path` la cartella che
contiene il `conftest.py` più esterno. La sola presenza di questo file basta
quindi a far funzionare `from app.core.config import ...` da qualunque cartella
si lanci la suite, senza installare il progetto né manipolare `sys.path` a mano.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PASSO 1.1 · 🟡 zona gialla · briefing docs/passi/1.1.md
# Qui c'è il cartello 5. Cancellalo quando l'hai fatto, insieme a questa
# intestazione. Il docstring qui sopra resta: aggiungici una riga che dica
# perché questo file imposta ENV.
# ─────────────────────────────────────────────────────────────────────────────

# TODO(1.1/5) — i test dichiarano il proprio ambiente
#   Sintassi: `import os`, poi UNA riga a livello di modulo, fuori da qualunque
#     funzione. Le due forme possibili:
#       os.environ["NOME"] = "valore"             assegna sempre
#       os.environ.setdefault("NOME", "valore")   assegna solo se manca
#   Da scrivere: ENV, con il valore dell'enum Env pensato per i test.
#   Decisione — sempre, o solo se manca? Scegline una e scrivi il perché:
#     - sempre: i test girano nello stesso ambiente su ogni macchina e in CI,
#       qualunque cosa ci sia nella shell di chi li lancia;
#     - solo se manca: chi vuole può lanciarli in un altro ambiente, per
#       esempio con ENV=DEV davanti al comando, al prezzo di risultati che
#       cambiano da una macchina all'altra.
#   Perché: i settings si creano all'import di app.core.config (briefing 1.4).
#     pytest legge questo file PRIMA di importare i moduli di test, e in CI non
#     esiste nessun .env: senza questa riga l'import dell'app fallisce, e la
#     suite si ferma con "ERROR collecting" prima di eseguire un solo test.
#   Trappola: in una fixture sarebbe troppo tardi. Le fixture girano quando
#     parte un test, ma l'app viene importata prima, durante la collection.
