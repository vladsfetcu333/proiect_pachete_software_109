/* ==========================================================================
   Proiect Pachete Software - Partea SAS
   Tema: Analiza performantei unui magazin online si posibilitati de extindere
   Autori: Sfetcu Vlad Andrei si Simion David, grupa 1094

   Inainte de rulare, modificati project_path daca proiectul este mutat.
   ========================================================================== */

options nodate nonumber;
ods graphics on;

%let project_path=C:\Users\Vlad_Sfetcu\Desktop\Pachete_software\proiect_pachete_software;
%let data_file=&project_path.\data\online_retail_project.csv;
%let out_path=&project_path.\sas\output;

libname out "&out_path.";

/* 1. Crearea unui set de date SAS din fisier extern */
proc import datafile="&data_file."
    out=work.retail_raw
    dbms=csv
    replace;
    guessingrows=max;
    getnames=yes;
run;

/* 2. Formate definite de utilizator */
proc format;
    value revfmt
        low - <0 = "Retur / valoare negativa"
        0 - <50 = "Comanda mica"
        50 - <150 = "Comanda medie"
        150 - high = "Comanda mare";
    value qtyfmt
        low - <0 = "Retur"
        0 - 5 = "Cantitate redusa"
        6 - 20 = "Cantitate normala"
        21 - high = "Cantitate ridicata";
    value $regionfmt
        "United Kingdom", "EIRE" = "UK si Irlanda"
        "Germany", "France", "Spain", "Netherlands", "Belgium", "Switzerland",
        "Portugal", "Norway", "Italy", "Finland", "Sweden", "Austria",
        "Denmark", "Poland", "Greece", "Czech Republic" = "Europa"
        "USA", "Canada" = "America de Nord"
        other = "Alte piete";
run;

/* 3. Procesare iterativa si conditionala + 4. functii SAS */
data work.retail_clean;
    length Region $20 TransactionType $6 HighValueFlag $3;
    set work.retail_raw;
    format InvoiceDate_dt datetime19. Revenue revfmt. Quantity qtyfmt. Country $regionfmt.;

    InvoiceDate_dt = input(InvoiceDate, anydtdtm.);
    Month = month(datepart(InvoiceDate_dt));
    Year = year(datepart(InvoiceDate_dt));
    WeekDay = weekday(datepart(InvoiceDate_dt));
    Revenue = Quantity * Price;
    RevenueNetCalc = Quantity * Price * (1 - Discount) + ShippingCost;
    Region = put(Country, $regionfmt.);

    if missing(Description) then Description = "Unknown";
    if missing(CustomerID) then CustomerMissing = 1;
    else CustomerMissing = 0;

    if Quantity < 0 then TransactionType = "Return";
    else TransactionType = "Sale";

    if Revenue >= 150 then HighValueFlag = "Da";
    else HighValueFlag = "Nu";

    /* exemplu de procesare iterativa: scor simplu pentru potential comercial */
    PotentialScore = 0;
    array components[3] Quantity Price Revenue;
    do i = 1 to dim(components);
        if components[i] > 0 then PotentialScore + 1;
    end;
    drop i;
run;

/* 5. Crearea de subseturi de date */
data work.sales work.returns work.customers_known;
    set work.retail_clean;
    if TransactionType = "Sale" then output work.sales;
    if TransactionType = "Return" then output work.returns;
    if CustomerMissing = 0 then output work.customers_known;
run;

/* 6. Combinarea seturilor de date prin PROC SQL */
proc sql;
    create table work.country_summary as
    select Country,
           Region,
           count(*) as NrLinii,
           count(distinct Invoice) as NrComenzi,
           count(distinct CustomerID) as NrClienti,
           sum(Revenue) as TotalRevenue format=comma14.2,
           mean(Revenue) as AvgRevenue format=comma10.2,
           calculated TotalRevenue / calculated NrClienti as RevenuePerClient format=comma12.2
    from work.sales
    where CustomerMissing = 0
    group by Country, Region
    order by TotalRevenue desc;

    create table work.product_summary as
    select Category,
           Description,
           sum(Quantity) as TotalQuantity,
           sum(Revenue) as TotalRevenue format=comma14.2,
           mean(Price) as AvgPrice format=comma10.2
    from work.sales
    group by Category, Description
    order by TotalRevenue desc;

    create table work.sales_enriched as
    select a.*, b.TotalRevenue as CountryRevenue format=comma14.2,
           b.RevenuePerClient
    from work.sales as a
    left join work.country_summary as b
      on a.Country = b.Country;
quit;

/* 7. Utilizarea de proceduri pentru raportare */
title "Top tari dupa venituri";
proc print data=work.country_summary(obs=10) label noobs;
    var Country Region NrComenzi NrClienti TotalRevenue RevenuePerClient;
    label Country="Tara" Region="Regiune" NrComenzi="Nr. comenzi"
          NrClienti="Nr. clienti" TotalRevenue="Venit total"
          RevenuePerClient="Venit/client";
run;

title "Raport pe regiuni";
proc report data=work.country_summary nowd;
    column Region NrComenzi NrClienti TotalRevenue RevenuePerClient;
    define Region / group "Regiune";
    define NrComenzi / sum "Comenzi";
    define NrClienti / sum "Clienti";
    define TotalRevenue / sum "Venit total";
    define RevenuePerClient / mean "Venit mediu/client";
run;

/* 8. Proceduri statistice */
title "Statistici descriptive pentru vanzari";
proc means data=work.sales n mean median std min p25 p75 max maxdec=2;
    var Quantity Price Revenue Discount ShippingCost;
run;

title "Corelatii intre variabilele numerice";
proc corr data=work.sales nosimple;
    var Quantity Price Revenue Discount ShippingCost;
run;

title "Regresie multipla: factorii care influenteaza venitul";
proc reg data=work.sales;
    model Revenue = Quantity Price Discount ShippingCost / vif;
run;
quit;

/* 9. Generarea de grafice */
title "Venituri totale pe tari";
proc sgplot data=work.country_summary(obs=12);
    vbar Country / response=TotalRevenue datalabel;
    xaxis fitpolicy=rotate label="Tara";
    yaxis label="Venit total";
run;

title "Distributia veniturilor pe comenzi";
proc sgplot data=work.sales;
    histogram Revenue;
    density Revenue;
    xaxis label="Revenue";
run;

/* 10. SAS ML: clusterizare clienti prin PROC FASTCLUS */
proc sql;
    create table work.rfm as
    select CustomerID,
           intck("day", max(datepart(InvoiceDate_dt)), today()) as Recency,
           count(distinct Invoice) as Frequency,
           sum(Revenue) as Monetary
    from work.sales
    where CustomerMissing = 0
    group by CustomerID;
quit;

proc stdize data=work.rfm out=work.rfm_scaled method=std;
    var Recency Frequency Monetary;
run;

title "Clusterizare clienti RFM";
proc fastclus data=work.rfm_scaled out=work.rfm_clusters maxclusters=4 maxiter=100;
    var Recency Frequency Monetary;
run;

proc sql;
    create table out.country_summary as select * from work.country_summary;
    create table out.product_summary as select * from work.product_summary(obs=25);
    create table out.rfm_clusters as select * from work.rfm_clusters;
quit;

ods graphics off;
title;
