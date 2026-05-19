import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Analiza Performantei unui Magazin Online",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
section[data-testid="stSidebar"] { background:#0F172A; border-right:1px solid #1E3A5F; }
section[data-testid="stSidebar"] * { color:#CBD5E1 !important; }
.main .block-container { padding:2rem 2.5rem 3rem; max-width:1200px; }
</style>
""", unsafe_allow_html=True)

section = st.sidebar.radio("Navigati la:",
                           ["1. Prezentare Date",
                            "2. Valori Lipsa si Extreme",
                            "3. Codificarea Datelor",
                            "4. Scalarea Datelor",
                            "5. Prelucrari Pandas",
                            "6. Reprezentari Grafice",
                            "7. Geopandas - Harta Vanzarilor",
                            "8. Clusterizare K-Means (RFM)",
                            "9. Regresie Logistica",
                            "10. Regresie Multipla"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset:** online_retail_project.csv")
st.sidebar.markdown("**Sursa:** set de date sintetic realist, inclus in proiect")


@st.cache_data
def load_data():
    candidate_files = [
        ("data/online_retail_project.csv", "csv"),
        ("online_retail_project.csv", "csv"),
        ("online_retail_II.xlsx", "excel"),
        ("online_retail_II.csv", "csv"),
    ]

    loaded = False
    df = None
    for path, file_type in candidate_files:
        try:
            if file_type == "excel":
                df = pd.read_excel(path, sheet_name="Year 2010-2011")
            else:
                df = pd.read_csv(path, encoding='utf-8')
            loaded = True
            break
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding='latin-1')
            loaded = True
            break
        except FileNotFoundError:
            continue

    if not loaded:
        st.error("Fisierul de date nu a fost gasit. Rulati scripts/generate_dataset.py sau plasati "
                 "data/online_retail_project.csv in directorul proiectului.")
        st.stop()

    df.columns = df.columns.str.strip()

    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

    if 'Quantity' in df.columns and 'Price' in df.columns:
        df['Revenue'] = df['Quantity'] * df['Price']

    return df

df_original = load_data()


if section == "1. Prezentare Date":
    st.title("Analiza Performantei unui Magazin Online")
    st.markdown("""
    Acest proiect analizeaza performanta unui **magazin online din Marea Britanie** 
    specializat pe cadouri si decoratiuni, folosind un set de date sintetic realist
    cu tranzactii din perioada 2024-2025.
    
    **Dataset:** online_retail_project.csv, inclus in directorul `data/`.
    """)

    df = df_original.copy()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Tranzactii", value=f"{len(df):,}")
    with col2:
        st.metric(label="Clienti Unici", value=f"{df['CustomerID'].nunique():,}")
    with col3:
        st.metric(label="Produse Unice", value=f"{df['StockCode'].nunique():,}")
    with col4:
        st.metric(label="Tari", value=f"{df['Country'].nunique()}")

    st.subheader("Structura Setului de Date")
    st.write(f"**Dimensiuni:** {df.shape[0]} randuri x {df.shape[1]} coloane")

    st.write("**Tipuri de date:**")
    dtypes_df = pd.DataFrame(df.dtypes, columns=['Tip'])
    dtypes_df['Valori Non-Null'] = df.count().values
    st.dataframe(dtypes_df.T)

    st.subheader("Statistici Descriptive")
    st.dataframe(df.describe())

    st.subheader("Primele Inregistrari")
    st.dataframe(df.head(10))

    st.subheader("Clasificarea Coloanelor")
    col1, col2 = st.columns(2)
    with col1:
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        st.write("**Coloane numerice:**")
        st.write(num_cols)
    with col2:
        cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
        st.write("**Coloane categorice:**")
        st.write(cat_cols)


elif section == "2. Valori Lipsa si Extreme":
    st.title("Tratarea Valorilor Lipsa si a Valorilor Extreme")

    df = df_original.copy()

    st.subheader("Analiza Valorilor Lipsa")

    total = df.isnull().sum().sort_values(ascending=False)
    percent = (df.isnull().sum() * 100 / df.isnull().count()).sort_values(ascending=False)
    missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Procent (%)'])
    st.dataframe(missing_data)

    missing_df = missing_data[missing_data['Total'] > 0]
    if len(missing_df) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        missing_df['Procent (%)'].plot(kind='barh', color='orange', ax=ax)
        ax.set_title('Procentul valorilor lipsa per coloana')
        ax.set_xlabel('Procent (%)')
        ax.set_ylabel('Coloana')
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        st.pyplot(fig)

    st.subheader("Cod Utilizat")
    st.code("""
total = df.isnull().sum().sort_values(ascending=False)
percent = (df.isnull().sum() * 100 / df.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Procent (%)'])
print(missing_data)
    """, language="python")

    st.subheader("Tratarea Valorilor Lipsa")
    st.write("""
    - **Description** (descrierea produsului): valorile lipsa se inlocuiesc cu 'Unknown'
    - **CustomerID**: valorile lipsa se elimina deoarece nu putem identifica clientul
    """)

    df['Description'] = df['Description'].fillna('Unknown')
    df_clean = df.dropna(subset=['CustomerID'])

    st.write(f"**Inainte de curatare:** {len(df)} randuri")
    st.write(f"**Dupa curatare:** {len(df_clean)} randuri")
    st.write(f"**Randuri eliminate:** {len(df) - len(df_clean)}")

    st.code("""
df['Description'] = df['Description'].fillna('Unknown')
df_clean = df.dropna(subset=['CustomerID'])
    """, language="python")

    st.write("**Verificare valori lipsa dupa tratare:**")
    total_after = df_clean.isnull().sum().sort_values(ascending=False)
    percent_after = (df_clean.isnull().sum() * 100 / df_clean.isnull().count()).sort_values(ascending=False)
    missing_after = pd.concat([total_after, percent_after], axis=1, keys=['Total', 'Procent (%)'])
    st.dataframe(missing_after)

    st.subheader("Detectarea Valorilor Extreme (Outlieri)")

    numerical_cols = ['Quantity', 'Price', 'Revenue']
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, col in enumerate(numerical_cols):
        if col in df_clean.columns:
            sns.boxplot(data=df_clean[col], ax=axes[i], color='skyblue')
            axes[i].set_title(f'Boxplot - {col}')
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Tratarea Outlierilor cu Metoda IQR")

    df_no_outliers = df_clean[(df_clean['Quantity'] > 0) & (df_clean['Price'] > 0)].copy()

    for col in ['Quantity', 'Price']:
        Q1 = df_no_outliers[col].quantile(0.25)
        Q3 = df_no_outliers[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        before = len(df_no_outliers)
        df_no_outliers = df_no_outliers[(df_no_outliers[col] >= lower) & (df_no_outliers[col] <= upper)]
        st.write(f"**{col}:** Q1={Q1:.2f}, Q3={Q3:.2f}, IQR={IQR:.2f}, "
                 f"Limite=[{lower:.2f}, {upper:.2f}], Eliminate: {before - len(df_no_outliers)}")

    st.code("""
Q1 = df[col].quantile(0.25)
Q3 = df[col].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
df = df[(df[col] >= lower) & (df[col] <= upper)]
    """, language="python")

    st.write("**Boxplot-uri dupa eliminarea outlierilor:**")
    df_no_outliers['Revenue'] = df_no_outliers['Quantity'] * df_no_outliers['Price']
    fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))
    for i, col in enumerate(['Quantity', 'Price', 'Revenue']):
        sns.boxplot(data=df_no_outliers[col], ax=axes2[i], color='lightgreen')
        axes2[i].set_title(f'Boxplot (fara outlieri) - {col}')
    plt.tight_layout()
    st.pyplot(fig2)


elif section == "3. Codificarea Datelor":
    st.title("Metode de Codificare a Datelor")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]

    from sklearn import preprocessing

    st.subheader("Label Encoding")
    st.write("Label Encoding converteste fiecare valoare categorica intr-un numar intreg.")

    le = preprocessing.LabelEncoder()
    top_countries = df['Country'].value_counts().head(10).index.tolist()
    df_top = df[df['Country'].isin(top_countries)].copy()
    df_top['Country_Encoded'] = le.fit_transform(df_top['Country'])

    st.write("**Mapping Label Encoding (top 10 tari):**")
    mapping = pd.DataFrame({'Country': le.classes_, 'Cod': range(len(le.classes_))})
    st.dataframe(mapping)

    st.code("""
from sklearn import preprocessing
le = preprocessing.LabelEncoder()
df['Country_Encoded'] = le.fit_transform(df['Country'])
    """, language="python")

    st.subheader("One-Hot Encoding")
    st.write("One-Hot Encoding creeaza o coloana noua pentru fiecare valoare unica, cu valori de 0 sau 1.")

    df_onehot = pd.get_dummies(df_top[['Country']].head(20), columns=['Country'], prefix='Country')
    st.dataframe(df_onehot.head(10))

    st.code("""
df_onehot = pd.get_dummies(df[['Country']], columns=['Country'], prefix='Country')
    """, language="python")

    st.subheader("Comparatie intre metode")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Label Encoding:**")
        st.write("- Avantaj: O singura coloana")
        st.write("- Dezavantaj: Implica o ordine artificiala")
    with col2:
        st.write("**One-Hot Encoding:**")
        st.write("- Avantaj: Nu implica ordine")
        st.write("- Dezavantaj: Multe coloane noi")


elif section == "4. Scalarea Datelor":
    st.title("Metode de Scalare a Datelor")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    numerical_data = df[['Quantity', 'Price', 'Revenue']].head(1000)

    from sklearn.preprocessing import StandardScaler, MinMaxScaler

    st.subheader("StandardScaler (Standardizare)")
    st.write("Aduce datele la o distributie cu **media 0** si **deviatia standard 1**.")

    scaler_std = StandardScaler()
    data_standardized = pd.DataFrame(scaler_std.fit_transform(numerical_data), columns=numerical_data.columns)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Date originale:**")
        st.dataframe(numerical_data.describe())
    with col2:
        st.write("**Date standardizate:**")
        st.dataframe(data_standardized.describe())

    st.code("""
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
data_scaled = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    """, language="python")

    st.subheader("MinMaxScaler (Normalizare)")
    st.write("Aduce valorile in intervalul **[0, 1]**.")

    scaler_mm = MinMaxScaler()
    data_normalized = pd.DataFrame(scaler_mm.fit_transform(numerical_data), columns=numerical_data.columns)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Date originale:**")
        st.dataframe(numerical_data.describe())
    with col2:
        st.write("**Date normalizate (MinMax):**")
        st.dataframe(data_normalized.describe())

    st.code("""
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)
    """, language="python")

    st.subheader("Vizualizare Comparativa")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].hist(numerical_data['Price'], bins=30, color='blue', edgecolor='black', alpha=0.7)
    axes[0].set_title('Price - Original')
    axes[1].hist(data_standardized['Price'], bins=30, color='green', edgecolor='black', alpha=0.7)
    axes[1].set_title('Price - StandardScaler')
    axes[2].hist(data_normalized['Price'], bins=30, color='orange', edgecolor='black', alpha=0.7)
    axes[2].set_title('Price - MinMaxScaler')
    plt.tight_layout()
    st.pyplot(fig)


elif section == "5. Prelucrari Pandas":
    st.title("Prelucrari Statistice, Gruparea si Agregarea Datelor")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Month'] = df['InvoiceDate'].dt.to_period('M').astype(str)

    st.subheader("Statistici Simple")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"£{df['Revenue'].sum():,.2f}")
    with col2:
        st.metric("Pret Mediu", f"£{df['Price'].mean():,.2f}")
    with col3:
        st.metric("Cantitate Maxima", f"{df['Quantity'].max():,}")

    st.code("""
total_revenue = df['Revenue'].sum()
avg_price = df['Price'].mean()
max_quantity = df['Quantity'].max()
    """, language="python")

    st.subheader("Vanzari pe Tara (GroupBy)")
    revenue_by_country = df.groupby('Country')['Revenue'].agg(['sum', 'mean', 'count']).rename(
        columns={'sum': 'Total Revenue', 'mean': 'Revenue Mediu', 'count': 'Nr Tranzactii'}
    ).sort_values('Total Revenue', ascending=False)
    st.dataframe(revenue_by_country.head(10))

    st.code("""
revenue_by_country = df.groupby('Country')['Revenue'].agg(['sum', 'mean', 'count'])
    """, language="python")

    st.subheader("Evolutia Vanzarilor pe Luni")
    monthly_revenue = df.groupby('Month')['Revenue'].sum()
    st.line_chart(monthly_revenue)

    st.subheader("Agregari Complexe")
    agg_result = df.groupby('Country').agg({
        'Revenue': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'CustomerID': 'nunique'
    }).sort_values(('Revenue', 'sum'), ascending=False).head(10)
    st.dataframe(agg_result)

    st.code("""
agg_result = df.groupby('Country').agg({
    'Revenue': ['sum', 'mean', 'count'],
    'Quantity': ['sum', 'mean'],
    'CustomerID': 'nunique'
})
    """, language="python")

    st.subheader("Distributia Tranzactiilor pe Tari")
    country_counts = df['Country'].value_counts().head(10)
    st.bar_chart(country_counts)

    st.subheader("Top 10 Produse dupa Revenue")
    top_products = df.groupby('Description')['Revenue'].sum().sort_values(ascending=False).head(10)
    st.dataframe(top_products)


elif section == "6. Reprezentari Grafice":
    st.title("Reprezentari Grafice")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']
    df['Month'] = df['InvoiceDate'].dt.to_period('M').astype(str)

    st.subheader("Histograma Distributiei Preturilor")
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.hist(df['Price'], bins=50, color='blue', edgecolor='black')
    plt.title('Distributia Preturilor')
    plt.xlabel('Pret')
    plt.ylabel('Frecventa')
    plt.tight_layout()
    st.pyplot(fig)

    st.code("""
plt.hist(df['Price'], bins=50, color='blue', edgecolor='black')
plt.title('Distributia Preturilor')
plt.show()
    """, language="python")

    st.subheader("Revenue Mediu pe Tara (Top 10)")
    avg_rev_country = df.groupby('Country')['Revenue'].mean().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    avg_rev_country.plot(kind='bar', color='skyblue', edgecolor='black', ax=ax2)
    plt.title('Revenue Mediu pe Tara')
    plt.xlabel('Tara')
    plt.ylabel('Revenue Mediu')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)

    st.subheader("Distributia Vanzarilor pe Top 5 Tari")
    top5_revenue = df.groupby('Country')['Revenue'].sum().sort_values(ascending=False).head(5)
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    plt.pie(top5_revenue, labels=top5_revenue.index, autopct='%1.1f%%', startangle=90)
    plt.title("Distributia Vanzarilor pe Top 5 Tari")
    plt.tight_layout()
    st.pyplot(fig3)

    st.subheader("Distributiile Variabilelor Numerice")
    numerical_cols = ['Quantity', 'Price', 'Revenue']
    fig4, axes4 = plt.subplots(1, 3, figsize=(18, 4))
    for i, col in enumerate(numerical_cols):
        axes4[i].hist(df[col].dropna(), bins=30, edgecolor='black', color='skyblue')
        axes4[i].set_title(f'Distributia: {col}')
        axes4[i].set_xlabel(col)
        axes4[i].set_ylabel('Frecventa')
    plt.tight_layout()
    st.pyplot(fig4)

    st.subheader("Matricea de Corelatie")
    corr_data = df[['Quantity', 'Price', 'Revenue']].corr()
    fig5, ax5 = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_data, annot=True, fmt=".2f", square=True, linewidths=0.5, ax=ax5)
    plt.title('Heatmap - Corelatia intre Variabile')
    plt.tight_layout()
    st.pyplot(fig5)

    st.subheader("Evolutia Vanzarilor Lunare")
    monthly = df.groupby(df['InvoiceDate'].dt.to_period('M').astype(str))['Revenue'].sum()
    st.line_chart(monthly)


elif section == "7. Geopandas - Harta Vanzarilor":
    st.title("Analiza Geografica a Vanzarilor cu Geopandas")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']

    revenue_by_country = df.groupby('Country')['Revenue'].sum().reset_index()
    revenue_by_country.columns = ['Country', 'TotalRevenue']

    st.subheader("Vanzari Totale pe Tari")
    st.dataframe(revenue_by_country.sort_values('TotalRevenue', ascending=False))

    try:
        import geopandas as gpd

        world = None
        try:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        except Exception:
            pass

        if world is None:
            try:
                import geodatasets
                world = gpd.read_file(geodatasets.data.naturalearth.land110["path"])
            except Exception:
                pass

        if world is None:
            world = gpd.read_file("https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip")
            if 'name' not in world.columns and 'NAME' in world.columns:
                world.rename(columns={'NAME': 'name'}, inplace=True)

        country_mapping = {
            'United Kingdom': 'United Kingdom',
            'Germany': 'Germany',
            'France': 'France',
            'EIRE': 'Ireland',
            'Spain': 'Spain',
            'Netherlands': 'Netherlands',
            'Belgium': 'Belgium',
            'Switzerland': 'Switzerland',
            'Portugal': 'Portugal',
            'Australia': 'Australia',
            'Norway': 'Norway',
            'Italy': 'Italy',
            'Channel Islands': 'United Kingdom',
            'Finland': 'Finland',
            'Cyprus': 'Cyprus',
            'Sweden': 'Sweden',
            'Austria': 'Austria',
            'Denmark': 'Denmark',
            'Japan': 'Japan',
            'Poland': 'Poland',
            'Israel': 'Israel',
            'USA': 'United States of America',
            'Singapore': 'Singapore',
            'Iceland': 'Iceland',
            'Canada': 'Canada',
            'Greece': 'Greece',
            'Malta': 'Malta',
            'Czech Republic': 'Czechia',
            'RSA': 'South Africa',
            'Saudi Arabia': 'Saudi Arabia',
            'European Community': 'France',
            'Bahrain': 'Bahrain',
            'Lithuania': 'Lithuania',
            'Brazil': 'Brazil',
            'Lebanon': 'Lebanon',
            'United Arab Emirates': 'United Arab Emirates'
        }

        revenue_by_country['Country_Mapped'] = revenue_by_country['Country'].map(country_mapping)
        revenue_by_country['Country_Mapped'] = revenue_by_country['Country_Mapped'].fillna(revenue_by_country['Country'])

        world_revenue = world.merge(revenue_by_country, left_on='name', right_on='Country_Mapped', how='left')

        st.subheader("Harta Vanzarilor - Europa")
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        world_revenue.plot(column='TotalRevenue', ax=ax, legend=True,
                           legend_kwds={'label': "Revenue Total", 'orientation': "horizontal"},
                           cmap='YlOrRd', missing_kwds={'color': 'lightgrey'},
                           edgecolor='black', linewidth=0.5)
        ax.set_xlim(-25, 45)
        ax.set_ylim(34, 72)
        ax.set_title('Distributia Vanzarilor in Europa', fontsize=14)
        ax.set_xlabel('Longitudine')
        ax.set_ylabel('Latitudine')
        plt.tight_layout()
        st.pyplot(fig)

        st.subheader("Harta Vanzarilor - Global")
        fig2, ax2 = plt.subplots(1, 1, figsize=(15, 8))
        world_revenue.plot(column='TotalRevenue', ax=ax2, legend=True,
                           legend_kwds={'label': "Revenue Total", 'orientation': "horizontal"},
                           cmap='YlOrRd', missing_kwds={'color': 'lightgrey'},
                           edgecolor='black', linewidth=0.3)
        ax2.set_title('Distributia Globala a Vanzarilor', fontsize=14)
        plt.tight_layout()
        st.pyplot(fig2)

        st.code("""
import geopandas as gpd
import geodatasets

world = gpd.read_file(geodatasets.data.naturalearth.land110["path"])
world_revenue = world.merge(revenue_by_country, left_on='name', right_on='Country_Mapped', how='left')
world_revenue.plot(column='TotalRevenue', legend=True, cmap='YlOrRd',
                   missing_kwds={'color': 'lightgrey'})
plt.title('Distributia Vanzarilor')
plt.show()
        """, language="python")

        st.subheader("Interpretare Economica")
        top3 = revenue_by_country.sort_values('TotalRevenue', ascending=False).head(3)
        st.write("**Top 3 piete dupa venituri:**")
        for _, row in top3.iterrows():
            st.write(f"- **{row['Country']}**: {row['TotalRevenue']:,.2f}")

        st.write("""
        **Posibilitati de extindere:** Tarile din Europa cu vanzari scazute 
        reprezinta piete potentiale de extindere pentru magazinul online, 
        datorita proximitatii geografice si a pietei comune UE.
        """)

    except ImportError as e:
        st.warning(f"Pachet lipsa: {e}. Rulati: pip install geopandas geodatasets")
    except Exception as e:
        st.warning(f"Eroare la generarea hartii: {e}")
        st.write("Datele sunt afisate sub forma de tabel mai sus.")


elif section == "8. Clusterizare K-Means (RFM)":
    st.title("Segmentarea Clientilor - K-Means Clustering (RFM)")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']

    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score

    st.subheader("Calculul Indicatorilor RFM")
    st.write("""
    - **R (Recency):** Cat de recent a cumparat clientul
    - **F (Frequency):** Cate comenzi a plasat clientul
    - **M (Monetary):** Cat a cheltuit clientul in total
    """)

    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'Invoice': 'nunique',
        'Revenue': 'sum'
    }).rename(columns={'InvoiceDate': 'Recency', 'Invoice': 'Frequency', 'Revenue': 'Monetary'})

    st.write("**Primele inregistrari RFM:**")
    st.dataframe(rfm.head(10))
    st.write("**Statistici descriptive RFM:**")
    st.dataframe(rfm.describe())

    st.code("""
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'Invoice': 'nunique',
    'Revenue': 'sum'
})
    """, language="python")

    st.subheader("Scalarea Datelor RFM")
    scaler = StandardScaler()
    rfm_scaled = pd.DataFrame(scaler.fit_transform(rfm), columns=rfm.columns)

    st.code("""
scaler = StandardScaler()
rfm_scaled = pd.DataFrame(scaler.fit_transform(rfm), columns=rfm.columns)
    """, language="python")

    st.subheader("Metoda Elbow")
    X = rfm_scaled.values
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(x=range(1, 11), y=wcss, marker='o', color='red')
    plt.title('The Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')
    plt.tight_layout()
    st.pyplot(fig)

    st.code("""
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)

sns.lineplot(x=range(1, 11), y=wcss, marker='o', color='red')
plt.title('The Elbow Method')
plt.show()
    """, language="python")

    n_clusters = st.slider("Selecteaza numarul de clustere:", 2, 8, 4)
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
    y_kmeans = kmeans.fit_predict(X)
    rfm['Cluster'] = y_kmeans

    st.subheader("Vizualizarea Clusterelor")
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    colors = ['yellow', 'blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']
    for i in range(n_clusters):
        sns.scatterplot(x=X[y_kmeans == i, 1], y=X[y_kmeans == i, 2],
                        color=colors[i % len(colors)], label=f'Cluster {i + 1}', s=50, ax=ax2)
    sns.scatterplot(x=kmeans.cluster_centers_[:, 1], y=kmeans.cluster_centers_[:, 2],
                    color='black', label='Centroizi', s=300, marker=',', ax=ax2)
    plt.grid(False)
    plt.title('Clustere de Clienti (Frequency vs Monetary)')
    plt.xlabel('Frequency (scalat)')
    plt.ylabel('Monetary (scalat)')
    plt.legend()
    plt.tight_layout()
    st.pyplot(fig2)

    st.subheader("Evaluarea Modelului K-Means")
    sil_score = silhouette_score(X, y_kmeans)
    st.write(f"**Silhouette Score:** {sil_score:.4f}")

    st.write("Silhouette Score pentru diferite valori ale lui k:")
    for k in range(2, 9):
        km = KMeans(n_clusters=k, init='k-means++', random_state=42)
        preds = km.fit_predict(X)
        score = silhouette_score(X, preds)
        st.write(f"k = {k} --> silhouette score = {score:.4f}")

    st.subheader("Profilul Clusterelor")
    cluster_profile = rfm.groupby('Cluster').agg({'Recency': 'mean', 'Frequency': 'mean', 'Monetary': 'mean'}).round(2)
    cluster_profile['Nr Clienti'] = rfm.groupby('Cluster').size()
    st.dataframe(cluster_profile)

    st.subheader("Interpretare Economica")
    st.write("""
    Segmentarea clientilor prin analiza RFM permite identificarea diferitelor categorii de clienti:
    - **Clienti VIP:** Recency scazut, Frequency si Monetary ridicate
    - **Clienti la risc:** Recency ridicat (nu au mai cumparat recent)
    - **Clienti noi:** Frequency scazut dar Recency recent
    - **Clienti ocazionali:** Frequency si Monetary scazute
    
    Aceste segmente ajuta la definirea strategiilor de marketing personalizate.
    """)


elif section == "9. Regresie Logistica":
    st.title("Regresie Logistica - Predictia Revenirii Clientului")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import (confusion_matrix, classification_report,
                                  accuracy_score, f1_score, roc_auc_score, roc_curve)

    st.subheader("Pregatirea Datelor pentru Clasificare")

    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    midpoint = df['InvoiceDate'].min() + (df['InvoiceDate'].max() - df['InvoiceDate'].min()) / 2

    df_first = df[df['InvoiceDate'] <= midpoint]
    df_second = df[df['InvoiceDate'] > midpoint]
    returned_customers = df_second['CustomerID'].unique()

    customer_features = df_first.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (midpoint - x.max()).days,
        'Invoice': 'nunique',
        'Revenue': ['sum', 'mean'],
        'Quantity': ['sum', 'mean'],
        'Country': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown'
    })
    customer_features.columns = ['Recency', 'Frequency', 'TotalRevenue',
                                  'AvgRevenue', 'TotalQuantity', 'AvgQuantity', 'Country']
    customer_features['Returned'] = customer_features.index.isin(returned_customers).astype(int)

    st.write(f"**Total clienti:** {len(customer_features)}")
    st.write(f"**Clienti care au revenit:** {customer_features['Returned'].sum()}")
    st.write(f"**Clienti care NU au revenit:** {(customer_features['Returned'] == 0).sum()}")
    st.dataframe(customer_features.head(10))

    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    customer_features['Country_Encoded'] = le.fit_transform(customer_features['Country'])

    X = customer_features[['Recency', 'Frequency', 'TotalRevenue',
                            'AvgRevenue', 'TotalQuantity', 'AvgQuantity', 'Country_Encoded']]
    y = customer_features['Returned']
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=10, test_size=.20)

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    st.code("""
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=10, test_size=.20)
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
    """, language="python")

    st.subheader("Antrenarea Modelului")
    RL = LogisticRegression(max_iter=100, penalty='l2', solver='lbfgs')
    RL.fit(X_train_scaled, y_train)
    y_predicted = RL.predict(X_test_scaled)

    st.code("""
RL = LogisticRegression(max_iter=100, penalty='l2', solver='lbfgs')
RL.fit(X_train_scaled, y_train)
y_predicted = RL.predict(X_test_scaled)
    """, language="python")

    st.subheader("Matricea de Confuzie")
    CM = confusion_matrix(y_test, y_predicted)
    fig, ax = plt.subplots(figsize=(5, 5))
    sns.heatmap(CM, annot=True, linewidths=0.5, linecolor="red", fmt=".0f", ax=ax)
    plt.xlabel("Valori Prezise")
    plt.ylabel("Valori Reale")
    plt.title("Matricea de Confuzie - Regresie Logistica")
    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("Raport de Clasificare")
    RL_report = classification_report(y_test, y_predicted)
    st.text(RL_report)

    acuratetea_RL = accuracy_score(y_test, y_predicted)
    f1 = f1_score(y_test, y_predicted, average='weighted')
    st.write(f"**Acuratetea modelului:** {acuratetea_RL:.4f}")
    st.write(f"**F1-Score:** {f1:.4f}")

    st.subheader("Curba ROC-AUC")
    try:
        ns_probs = [0 for _ in range(len(y_test))]
        model_probs = RL.predict_proba(X_test_scaled)[:, 1]
        ns_auc = roc_auc_score(y_test, ns_probs)
        lr_auc = roc_auc_score(y_test, model_probs)
        st.write(f"**No Skill: ROC AUC = {ns_auc:.3f}**")
        st.write(f"**Model: ROC AUC = {lr_auc:.3f}**")

        ns_fpr, ns_tpr, _ = roc_curve(y_test, ns_probs)
        model_fpr, model_tpr, _ = roc_curve(y_test, model_probs)
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        plt.plot(ns_fpr, ns_tpr, linestyle='--', label='No Skill')
        plt.plot(model_fpr, model_tpr, marker='.', label='Classifier')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Curba ROC-AUC')
        plt.legend()
        plt.tight_layout()
        st.pyplot(fig2)
    except Exception as e:
        st.warning(f"Nu s-a putut genera curba ROC: {e}")

    st.subheader("Interpretare Economica")
    st.write(f"""
    Modelul de regresie logistica prezice cu o acuratete de **{acuratetea_RL:.1%}** 
    daca un client va reveni la magazinul online. Aceasta permite:
    - **Campanii de retentie** targetate pentru clientii cu risc de pierdere
    - **Oferte personalizate** pentru stimularea revenirii
    - **Optimizarea bugetului de marketing** prin focusarea pe clientii potriviti
    """)


elif section == "10. Regresie Multipla":
    st.title("Regresie Multipla - Factorii care Influenteaza Valoarea Comenzii")

    df = df_original.copy()
    df = df.dropna(subset=['CustomerID'])
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    df['Revenue'] = df['Quantity'] * df['Price']

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    st.subheader("Pregatirea Datelor")

    invoice_data = df.groupby('Invoice').agg({
        'Quantity': 'sum', 'Price': 'mean', 'Revenue': 'sum',
        'StockCode': 'nunique', 'CustomerID': 'first',
        'Country': 'first', 'InvoiceDate': 'first'
    }).rename(columns={'Quantity': 'TotalQuantity', 'Price': 'AvgPrice',
                       'Revenue': 'TotalRevenue', 'StockCode': 'UniqueProducts'})

    invoice_data['DayOfWeek'] = invoice_data['InvoiceDate'].dt.dayofweek
    invoice_data['Hour'] = invoice_data['InvoiceDate'].dt.hour
    invoice_data['Month'] = invoice_data['InvoiceDate'].dt.month

    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    invoice_data['Country_Encoded'] = le.fit_transform(invoice_data['Country'])
    st.dataframe(invoice_data.head(10))

    X = invoice_data[['TotalQuantity', 'AvgPrice', 'UniqueProducts',
                       'DayOfWeek', 'Hour', 'Month', 'Country_Encoded']]
    y = invoice_data['TotalRevenue']

    st.subheader("Distributia Variabilei Target")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(y, kde=True, ax=ax)
        ax.set_title('Distributia Revenue (original)')
        plt.tight_layout()
        st.pyplot(fig)

    y_log = np.log1p(y)
    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.histplot(y_log, kde=True, ax=ax2)
        ax2.set_title('Distributia Revenue (log)')
        plt.tight_layout()
        st.pyplot(fig2)

    X_train, X_test, y_train, y_test = train_test_split(X, y_log, random_state=63, test_size=.20)

    st.subheader("Regresie Multipla cu Statsmodels")
    try:
        import statsmodels.api as sm
        X_train_sm = sm.add_constant(X_train)
        model_sm = sm.OLS(y_train, X_train_sm).fit()

        st.write("**Informatii Generale despre Model**")
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.metric("R-squared", f"{model_sm.rsquared:.4f}")
            st.metric("F-statistic", f"{model_sm.fvalue:.2f}")
            st.metric("Nr. Observatii", f"{int(model_sm.nobs):,}")
        with info_col2:
            st.metric("Adj. R-squared", f"{model_sm.rsquared_adj:.4f}")
            st.metric("Prob (F-statistic)", f"{model_sm.f_pvalue:.4f}")
            st.metric("Df Model", f"{int(model_sm.df_model)}")

        st.write("**Coeficientii Modelului**")
        coef_df = pd.DataFrame({
            'Variabila': model_sm.params.index,
            'Coeficient': model_sm.params.values,
            'Std Error': model_sm.bse.values,
            't-value': model_sm.tvalues.values,
            'P-value': model_sm.pvalues.values,
            'Interval Inf (2.5%)': model_sm.conf_int()[0].values,
            'Interval Sup (97.5%)': model_sm.conf_int()[1].values
        })
        coef_df['Semnificativ'] = coef_df['P-value'].apply(
            lambda p: 'Da' if p < 0.05 else 'Nu')
        st.dataframe(coef_df.style.format({
            'Coeficient': '{:.6f}',
            'Std Error': '{:.6f}',
            't-value': '{:.3f}',
            'P-value': '{:.4f}',
            'Interval Inf (2.5%)': '{:.4f}',
            'Interval Sup (97.5%)': '{:.4f}'
        }), use_container_width=True)

        st.write("**Teste de Diagnosticare**")
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            st.write(f"- **Durbin-Watson:** {sm.stats.stattools.durbin_watson(model_sm.resid):.3f}")
            st.write(f"- **Log-Likelihood:** {model_sm.llf:,.2f}")
            st.write(f"- **AIC:** {model_sm.aic:,.2f}")
        with diag_col2:
            st.write(f"- **BIC:** {model_sm.bic:,.2f}")
            st.write(f"- **Skew (reziduuri):** {model_sm.resid.skew():.3f}")
            st.write(f"- **Kurtosis (reziduuri):** {model_sm.resid.kurtosis():.3f}")

        with st.expander("Afiseaza output-ul complet OLS (text)"):
            st.text(str(model_sm.summary()))

        st.code("""
import statsmodels.api as sm
X_train_sm = sm.add_constant(X_train)
model_sm = sm.OLS(y_train, X_train_sm).fit()
print(model_sm.summary())
        """, language="python")

        X_test_sm = sm.add_constant(X_test)
        y_predicted_sm = model_sm.predict(X_test_sm)
    except ImportError:
        from sklearn import linear_model
        lr = linear_model.LinearRegression()
        model_lr = lr.fit(X_train, y_train)
        y_predicted_sm = model_lr.predict(X_test)

    st.subheader("Evaluarea Modelului")
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    plt.scatter(y_predicted_sm, y_test, alpha=0.5)
    plt.xlabel('Predicted Revenue (log)')
    plt.ylabel('Actual Revenue (log)')
    plt.title('Compararea Preturilor Prezise vs Reale')
    min_val = min(y_predicted_sm.min(), y_test.min())
    max_val = max(y_predicted_sm.max(), y_test.max())
    plt.plot([min_val, max_val], [min_val, max_val], color="red")
    plt.tight_layout()
    st.pyplot(fig3)

    mse = mean_squared_error(y_test, y_predicted_sm)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_predicted_sm)
    r2 = r2_score(y_test, y_predicted_sm)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("MSE", f"{mse:.4f}")
    with col2:
        st.metric("RMSE", f"{rmse:.4f}")
    with col3:
        st.metric("MAE", f"{mae:.4f}")
    with col4:
        st.metric("R2", f"{r2:.4f}")

    st.code("""
mse = mean_squared_error(y_test, y_predicted)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_predicted)
r2 = r2_score(y_test, y_predicted)
    """, language="python")

    st.subheader("Interpretare Economica")
    st.write(f"""
    Modelul de regresie multipla explica **{r2:.1%}** din variatia valorii comenzilor.
    
    **Factori care influenteaza valoarea comenzii:**
    - **Numarul de produse unice** din comanda are cel mai mare impact
    - **Cantitatea totala** influenteaza direct valoarea
    - **Pretul mediu** al produselor din comanda
    - **Ziua din saptamana** si **ora** comenzii au un impact mai mic
    
    **Recomandari:** Strategiile de cross-selling pot creste semnificativ valoarea medie a comenzii.
    """)
