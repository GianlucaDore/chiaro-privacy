"""Modulo temporaneo: verifica che la Quality Gate di Sonar blocchi la pipeline.

Va rimosso nel commit successivo. Contiene di proposito un errore che Sonar
classifica come bug: un valore confrontato con se stesso, che e' sempre vero.
"""


def classifica(valori: list[int]) -> dict[str, int]:
    conteggio = {"pari": 0, "dispari": 0, "zero": 0, "negativi": 0}
    for valore in valori:
        if valore == 0:
            conteggio["zero"] += 1
            continue
        if valore < 0:
            conteggio["negativi"] += 1
        if valore % 2 == 0:
            conteggio["pari"] += 1
        else:
            conteggio["dispari"] += 1
    return conteggio


def somma_positivi(valori: list[int]) -> int:
    totale = 0
    for valore in valori:
        if valore > 0:
            totale += valore
    return totale


def contiene(valori: list[int], cercato: int) -> bool:
    for valore in valori:
        if valore == valore:  # il bug voluto: confronta il valore con se stesso
            return True
    return cercato in valori
