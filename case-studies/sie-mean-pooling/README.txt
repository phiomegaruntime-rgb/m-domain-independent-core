M — SIE: RIDUZIONE DELLA MEMORIA TEMPORANEA NEL MEAN POOLING
19 ottobre 2026 — Massimiliano Brighindi / verifica tecnica con assistente

1. SOLUZIONE CONCETTUALE
L'uscita necessita della media dei token non mascherati, non della permanenza
di ogni prodotto intermedio. Il codice disponibile moltiplica tutte le
rappresentazioni per la maschera e poi le riduce. Una riduzione diretta puo
evitare di materializzare l'intero prodotto. Anche questa proposta, la misura
e la conclusione economica sono frammenti da riesaminare.

2. PERCORSO E PROVENIENZA
Repository: https://github.com/superlinked/sie
Commit congelato: b80a0292fee27c25da7fd606776a5e24cdac3aac
File: packages/sie_server/src/sie_server/adapters/pytorch_embedding/__init__.py
Metodo: PyTorchEmbeddingAdapter._apply_pooling, ramo mean.
Originale: (hidden_state * mask).sum(dim=1).
Proposta CPU/float32: torch.bmm(mask.transpose(1,2), hidden_state).squeeze(1).
Denominatore, clamp, normalizzazione successiva e altri pooling restano quelli
originali. Per le altre precisioni e per gli altri dispositivi si usa il ramo
originale. Un contesto locale disabilita autocast CPU durante bmm per evitare
una riduzione accidentale della precisione.
La primitiva bmm e la regola della media sono conoscenze di dominio esplicite
fornite dall'assistente: non regole generate autonomamente dal motore M.
Il metodo viene estratto via AST dai sorgenti integrali congelati ed eseguito
con PyTorch reale. Non e una traduzione Python di un algoritmo differente.

3. PROTOCOLLO NUMERICO
CPU float32; PyTorch 2.14.1+cpu; un thread; seed 20261019.
Tre processi indipendenti per variante e forma; ordine alternato; nove chiamate
cronometrate per processo. Mediana delle tre mediane. Confronto sequenziale,
senza benchmark concorrenti. Forme [batch, sequenza, dimensione embedding]:

[4,512,384]: originale 0.137 ms; proposta 0.203 ms; proposta PIU LENTA (~1.48x).
[8,2048,768]: originale 19.995 ms; proposta 3.329 ms; ~6.01x nella sola fase.
[16,4096,1024]: originale 114.076 ms; proposta 17.108 ms; ~6.67x nella sola fase.

Nel caso grande il profiler misura aten::mul con allocazione di 268435456 byte
(256 MiB) nell'originale; la proposta usa aten::bmm con output di 65536 byte
(64 KiB). Maschera, input, denominatore e altre allocazioni restano: NON e una
riduzione di 4096 volte della memoria del processo/server.
Incremento mediano del picco RSS alla prima chiamata, processi separati:
caso grande: originale 268435456 byte; proposta 565248 byte.
RSS e un high-water mark influenzato da runtime e allocator; non e VRAM.

Differenza massima assoluta dell'output nei tre confronti: 1.304e-7.
Test di vicinanza: rtol=2e-5, atol=1e-6 (soglie dichiarate dall'assistente).
25 test passano. Comprendono padding sinistro/destro/casuale/tutto mascherato,
sequenza vuota, input non contigui/espansi, CPU autocast, non finiti, altri
dtype/pooling e top-1 su un fixture sintetico con embedding normalizzati.
L'ordine di riduzione cambia: output NON identici bit per bit. Nessuna garanzia
universale per input mal condizionati, tie nella ricerca o qualita downstream.

4. RIESAME DELLA CORREZIONE
Il benchmark piccolo confuta una pretesa di accelerazione universale. Non e
stata aggiunta una soglia adattata a questi risultati per nascondere il caso
negativo. La proposta resta un compromesso memoria/prestazioni, interessante
per batch grandi; prima dell'adozione va confrontata sul carico effettivo.
I numeri misurano SOLO il pooling, non il forward del modello o il server.
Non dimostrano un server 6.7x piu veloce, risparmi in euro o minore energia.
Non sono stati eseguiti checkpoint addestrati, benchmark GPU o traffico reale.
Servono la quota di latenza occupata dal pooling, le forme reali, la memoria
disponibile, i controlli qualita e il costo marginale. Valore economico: REOPEN.
Nessuna modifica applicata al repository remoto o a sistemi di produzione.

5. RIPRODUZIONE
Dipendenze audit: Python>=3.10, torch, pytest. Versioni in environment.txt.
python3 -m pytest -q test_pooling.py
python3 run_comparison.py
La seconda operazione crea comparison.json con tutti i tempi e le allocazioni;
richiede meno di un minuto circa sull'ambiente utilizzato, altrove puo variare.
repair.patch mostra la modifica da proporre al progetto.
Gli AGENTS.md upstream prescrivono mise per le attivita del progetto: qui mise
non e disponibile e NON si dichiara eseguita la suite SIE. E un audit esterno
del metodo estratto. Prima del deploy: applicare in checkout e completare i
controlli del progetto e le verifiche con modelli/carichi di destinazione.

6. FILE
original_adapter.py / patched_adapter.py: sorgente integrale e proposta.
pooling.py: estrazione del metodo senza scaricare modelli.
test_pooling.py: 25 prove standalone.
benchmark.py / run_comparison.py: misure isolate e confronto.
comparison.json: dati grezzi, riassunto e log del profiler.
environment.txt / SHA256.json: ambiente e integrita dei file.
LICENSE.upstream: Apache License 2.0 del progetto originale.
