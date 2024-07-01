#import pip
#pip.main(['install','pymsteams'])
import pandas as pd
import yfinance as yf


# Liste des entreprises du CAC 40 avec leurs secteurs
data = {
    "Nom": [
        "Accor", "Air Liquide", "Airbus", "ArcelorMittal", "Atos", "Bouygues", 
        "Capgemini", "Carrefour", "Danone", "Dassault Systèmes", "Engie", 
        "EssilorLuxottica", "Hermès", "Kering", "Legrand", "L'Oréal", 
        "LVMH", "Michelin", "Orange", "Renault", "Safran", 
        "Saint-Gobain", "Sanofi", "Schneider Electric", "Stellantis", 
        "STMicroelectronics", "Teleperformance", "Thales", "TotalEnergies", 
        "Unibail-Rodamco-Westfield", "Veolia", "Vinci", "Vivendi"
    ],
    "Secteur": [
        "Hôtellerie", "Gaz industriels", "Aérospatiale", "Acier", "Services informatiques", 
        "Construction", "Services informatiques", "Distribution", "Agroalimentaire", 
        "Logiciels", "Énergie", "Lunetterie", "Luxe", "Luxe", "Équipements électriques", 
        "Cosmétique", "Luxe", "Télécommunications", "Automobile", 
        "Automobile", "Aérospatiale", "Matériaux de construction", "Pharmaceutique", 
        "Équipements électriques", "Automobile", "Semi-conducteurs", "Services aux entreprises", 
        "Aérospatiale et Défense", "Énergie", "Immobilier", "Gestion de l'eau et des déchets", 
        "Construction", "Médias"
    ],
    "Ticker": [
        "AC.PA", "AI.PA", "AIR.PA", "MT.AS", "ATO.PA", "EN.PA", 
        "CAP.PA", "CA.PA", "BN.PA", "DSY.PA", "ENGI.PA", 
        "EL.PA", "RMS.PA", "KER.PA", "LR.PA", "OR.PA", 
        "MC.PA", "ML.PA", "ORA.PA", "RNO.PA", "SAF.PA", 
        "SGO.PA", "SAN.PA", "SU.PA", "STLAP.PA", 
        "STMPA.PA", "TEP.PA", "HO.PA", "TTE.PA", 
        "URW.PA", "VIE.PA", "DG.PA", "VIV.PA"
    ]
}

# Convertir en DataFrame
df_cac_40 = pd.DataFrame(data)

# Ajouter les colonnes pour le prix de l'action, le dividende, le volume d'achat et la comparaison des prix
df_cac_40['Prix'] = 0.0
df_cac_40['Dividende'] = 0.0
df_cac_40['Volume'] = 0
df_cac_40['PrixInf1Mois'] = False
df_cac_40['PrixInf3Mois'] = False
df_cac_40['PrixInf6Mois'] = False
df_cac_40['PrixInf12Mois'] = False

# Fonction pour récupérer les données financières
def obtenir_donnees_financieres(ticker):
    try:
        action = yf.Ticker(ticker)
        # Récupérer l'historique des 12 derniers mois
        hist_12m = action.history(period='1y')
        if hist_12m.empty:
            # Si les données des 12 derniers mois ne sont pas disponibles, récupérer les 6 derniers mois
            hist_6m = action.history(period='6mo')
            if hist_6m.empty:
                return None, None, None, None, None, None, None
            hist_12m = hist_6m
        
        prix_actuel = hist_12m['Close'].iloc[-1]
        dividende = action.info.get('dividendRate', 0.0)
        volume = hist_12m['Volume'].iloc[-1]
        
        # Récupérer les historiques des 1, 3 et 6 derniers mois
        hist_1m = hist_12m[hist_12m.index >= (hist_12m.index[-1] - pd.DateOffset(months=1))]
        hist_3m = hist_12m[hist_12m.index >= (hist_12m.index[-1] - pd.DateOffset(months=3))]
        hist_6m = hist_12m[hist_12m.index >= (hist_12m.index[-1] - pd.DateOffset(months=6))]
        
        prix_min_1_mois = hist_1m['Close'].min() if not hist_1m.empty else float('inf')
        prix_min_3_mois = hist_3m['Close'].min() if not hist_3m.empty else float('inf')
        prix_min_6_mois = hist_6m['Close'].min() if not hist_6m.empty else float('inf')
        prix_min_12_mois = hist_12m['Close'].min()
        
        prix_inf_1_mois = prix_actuel <= prix_min_1_mois
        prix_inf_3_mois = prix_actuel <= prix_min_3_mois
        prix_inf_6_mois = prix_actuel <= prix_min_6_mois
        prix_inf_12_mois = prix_actuel <= prix_min_12_mois
        prix_inf = prix_inf_1_mois | prix_inf_3_mois | prix_inf_6_mois | prix_inf_12_mois

        
        return prix_actuel, dividende, volume, prix_inf_1_mois, prix_inf_3_mois, prix_inf_6_mois, prix_inf_12_mois, prix_inf
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {ticker}: {e}")
        return None, None, None, None, None, None, None
    
def get_short_list():
# Remplir les colonnes avec les données financières
    for i, row in df_cac_40.iterrows():
        ticker = row['Ticker']
        prix, dividende, volume, prix_inf_1_mois, prix_inf_3_mois, prix_inf_6_mois, prix_inf_12_mois, prix_inf = obtenir_donnees_financieres(ticker)
        if prix is not None and dividende is not None and volume is not None:
            df_cac_40.at[i, 'Prix'] = prix
            df_cac_40.at[i, 'Dividende'] = dividende
            df_cac_40.at[i, 'Volume'] = volume
            df_cac_40.at[i, 'PrixInf1Mois'] = prix_inf_1_mois
            df_cac_40.at[i, 'PrixInf3Mois'] = prix_inf_3_mois
            df_cac_40.at[i, 'PrixInf6Mois'] = prix_inf_6_mois
            df_cac_40.at[i, 'PrixInf12Mois'] = prix_inf_12_mois
            df_cac_40.at[i, 'prix_inf'] = prix_inf
            df_cac_40['Dividend_Price_Ratio'] = 100* (df_cac_40['Dividende'] / df_cac_40['Prix'])
    return df_cac_40.sort_values(by=["prix_inf","Dividend_Price_Ratio"], ascending=False).set_index('Nom')[:6]
import requests
from bs4 import BeautifulSoup
from newspaper import Article

# URL of the webpage to be scraped
def get_news(url):
    # Fetch the content of the webpage
    response = requests.get(url)
    news_lst = []
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the container with the class "container-news-page"
        container = soup.find('div', class_='container-news-page')
        
        # Check if the container is found
        if container:
            # Find all news items within the container
            news_items = container.find_all('div', class_='news-item')
            
            # Prepare the content for display
            content = []
            for item in news_items:
                title = item.find('p', class_='news-item-title-text')
                source = item.find('span', class_='news-item-source-text')
                date = item.find('small', class_='news-item-date')
                hour = item.find('span', class_='news-item-hour-text')
                link = item.find('a', class_='news-item-link')['href']
                
                # Full URL of the news article
                article_url = f"https://bourse.fortuneo.fr{link}"
                
                # Use newspaper to fetch and parse the article
                article = Article(article_url)
                article.download()
                article.parse()
                article.nlp()
                
                content.append({
                    'title': title.get_text(strip=True) if title else 'No Title',
                    'source': source.get_text(strip=True) if source else 'No Source',
                    'date': date.get_text(strip=True) if date else 'No Date',
                    'hour': hour.get_text(strip=True) if hour else 'No Hour',
                    'text': article.summary,
                    "keywords" : article.keywords
                })
        else:
            print("Container with class 'container-news-page' not found.")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return content

import pymsteams
from datetime import datetime
import pandas_datareader.data as web
# URL of the webpage to be scraped
def send_analysis(df):
    report_sections = []
    for nom in df.index:
        # calculate report data
        dividend_ratio = round(df.loc[nom]["Dividend_Price_Ratio"], 2)
        p_variation = '<span style="color:#D61355">Prix haut</span>'
        if df.loc[nom]["PrixInf1Mois"] == True:
            p_variation = '<span style="color:#1F8A70">Prix inférieur 1 mois</span>'
        if df.loc[nom]["PrixInf3Mois"] == True:
            p_variation = '<span style="color:#1F8A70">Prix inférieur 3 mois</span>'
        if df.loc[nom]["PrixInf6Mois"] == True:
            p_variation = '<span style="color:#1F8A70">Prix inférieur 6 mois</span>'
        if df.loc[nom]["PrixInf12Mois"] == True:
            p_variation = '<span style="color:#1F8A70">Prix inférieur 12 mois</span>'
            
        close_price = f"{round(df.loc[nom]['Prix'], 2)}€" 
        volume  = f"{round(df.loc[nom]['Volume'], 4):,}" 
        div  = f"{round(df.loc[nom]['Dividend_Price_Ratio'], 2):,}%" 

        # Prepare section content
        text_ = f"""
        <span style="color: white; background-color: black;"> Sector : {df.loc[nom]['Secteur']} </span> <br>
        <span style="color: white; background-color: black;"> Close price : { close_price } </span> <br>
        <span style="color: white; background-color: black;"> Price variation : { p_variation } </span> <br>
        <span style="color: white; background-color: black;"> Volume { volume } </span> <br>
        <span style="color: white; background-color: black;"> Divdend Ratio { div } </span><br>
        """
        
        message_section = pymsteams.cardsection()
        message_section.activityTitle(nom) # Define section title
        message_section.activityImage("https://cdn-icons-png.flaticon.com/512/10310/10310226.png")
        message_section.activityText(text_) # Insert markdown text
        report_sections.append(message_section)
        
    stocks_report = pymsteams.connectorcard(hookurl="https://sasoffice365.webhook.office.com/webhookb2/e8b81be0-254b-482c-847a-dbe063bff6ed@b1c14d5c-3625-45b3-a430-9552373a0c2f/IncomingWebhook/1f94d95a428248ff8800de9a563461ed/119d6701-5864-4bd5-a1e1-0879d3169506")
    stocks_report.title(f"CAC40 STOCK REPORT")
    stocks_report.text(f"""
    Report automatically generated 
    Date: { datetime.today().strftime('%Y-%m-%d') }
    """)
    for section in report_sections:
        stocks_report.addSection(section)
        
    stocks_report.color('#000000')
    stocks_report.send()

# Function to send a message to Microsoft Teams
def send_to_teams(webhook_url, articles):
    teams_message = pymsteams.connectorcard(webhook_url)
    teams_message.text(f"""
    Date: { datetime.today().strftime('%Y-%m-%d') }
    """)
    found_words = []   
    for article in articles:
        found_words.append([word for word in data["Nom"] if word.lower() in article['text'].lower()])
        section = pymsteams.cardsection()
        section.title(article['title'])
        section.activitySubtitle(f"Source: {article['source']} | Date: {article['date']} | Hour: {article['hour']}")
        section.text(article['text']+"\n"+"***************************************************************************\n")
        teams_message.addSection(section)
    teams_message.title(f"Entreprises cités : {sum(found_words, [])}")

    teams_message.send()
    
url_actu = "https://bourse.fortuneo.fr/actualites/"
url = "https://bourse.fortuneo.fr/actualites/marches"
#news = get_news(url_actu)
news_marches = get_news(url)
webhook_url="https://sasoffice365.webhook.office.com/webhookb2/e8b81be0-254b-482c-847a-dbe063bff6ed@b1c14d5c-3625-45b3-a430-9552373a0c2f/IncomingWebhook/1f94d95a428248ff8800de9a563461ed/119d6701-5864-4bd5-a1e1-0879d3169506"
#send_to_teams(webhook_url=webhook_url, articles=news_marches)
send_to_teams(webhook_url=webhook_url, articles=news_marches)
