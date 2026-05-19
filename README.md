# Analiza performantei unui magazin online

Proiect Pachete Software - Python (Streamlit) si SAS.

Tema proiectului este analiza activitatii unui magazin online european si
identificarea unor posibilitati de extindere pe baza tranzactiilor, clientilor,
produselor si pietelor externe.

## Structura

```text
app.py                                      aplicatia Streamlit
data/online_retail_project.csv             setul de date inclus
sas/analiza_magazin_online.sas             partea SAS
docs/raport_proiect_pachete_software.docx  raport Word
docs/raport_proiect_pachete_software.pdf   raport PDF
scripts/generate_dataset.py                regenerare dataset
scripts/build_report.py                    regenerare raport
requirements.txt                           dependinte Python
```

## Cerinte acoperite in Python

- metode Streamlit pentru afisare, metrici, tabele si grafice;
- geopandas pentru harta vanzarilor;
- tratarea valorilor lipsa si extreme;
- codificarea datelor cu LabelEncoder si one-hot encoding;
- scalare cu StandardScaler si MinMaxScaler;
- pandas groupby, agg, statistici si agregari;
- scikit-learn pentru K-Means si regresie logistica;
- statsmodels pentru regresie multipla OLS.

## Cerinte acoperite in SAS

- import din fisier extern;
- formate definite de utilizator;
- procesare iterativa si conditionala;
- subseturi de date;
- functii SAS;
- PROC SQL si combinare de seturi;
- masive / arrays;
- proceduri de raportare;
- proceduri statistice si grafice;
- clusterizare cu PROC FASTCLUS.

## Instalare Python

```bash
pip install -r requirements.txt
```

## Rulare aplicatie Streamlit

```bash
streamlit run app.py
```

## Regenerare dataset si raport

```bash
python scripts/generate_dataset.py
python scripts/build_report.py
```

## Rulare SAS

Deschideti `sas/analiza_magazin_online.sas` in SAS Studio / SAS Enterprise
Guide / Base SAS si rulati scriptul. Daca mutati proiectul, modificati valoarea
macrovariabilei `project_path` din primele linii ale fisierului SAS.

## Autori

Sfetcu Vlad Andrei si Simion David, grupa 1094.

