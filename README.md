# PDF Text Replacement Tool

Utility da riga di comando per sostituire testo in un PDF creando un nuovo file, senza modificare il sorgente.

La sostituzione conserva, quando il font è incorporato nel PDF:

- famiglia e variante del font;
- dimensione;
- grassetto e corsivo;
- colore;
- linea di base e orientamento cardinale del testo.

Se il font originale non è incorporato, lo script usa un font PDF standard coerente con le caratteristiche disponibili (serif/sans-serif/monospaziato, normale/grassetto/corsivo).

## Requisiti

- Python 3.10 o successivo
- PyMuPDF

```bash
pip install pymupdf
```

## Utilizzo

```bash
python pdf_replace.py "TESTO_DA_CERCARE" "TESTO_NUOVO" "sorgente.pdf" "destinazione.pdf"
```

Il file di destinazione è facoltativo. Se viene omesso, viene creato automaticamente accanto al sorgente con il suffisso `_replaced`:

```bash
python pdf_replace.py "Mario Rossi" "Luigi Bianchi" "documento.pdf"
```

L'esempio genera `documento_replaced.pdf` e lascia `documento.pdf` invariato.

## Come funziona

1. Cerca tutte le occorrenze del testo in ogni pagina.
2. Rileva lo span tipografico che copre ogni occorrenza.
3. Estrae e registra il font incorporato nel PDF, inclusa la variante bold/italic.
4. Rimuove soltanto il testo originale tramite redaction, preservando immagini e grafica vettoriale.
5. Inserisce il nuovo testo sulla linea di base originale con dimensione, colore e orientamento rilevati.
6. Salva il risultato in un nuovo PDF; sorgente e destinazione non possono coincidere.

## Note

- Se il testo sostitutivo è molto più lungo dell'originale, può sovrapporsi ad altri elementi: la dimensione viene mantenuta intenzionalmente per rispettare la formattazione sorgente.
- Il matching di PyMuPDF non distingue maiuscole e minuscole.
- Per testi composti da più stili, viene mantenuto lo stile dello span che occupa la parte maggiore dell'occorrenza.

## Licenza

MIT
