import pandas as pd

def convert_to_sek(trades_file, valuta_file):
    trades_df = pd.read_csv(trades_file, sep=",", header=0, encoding='utf-8', 
                       names=["Symbol","Buy/Sell","Quantity","TradePrice","IBCommission","CurrencyPrimary","TradeDate"])
    valuta_df = pd.read_csv(valuta_file, sep=";", header=0, encoding='utf-8', 
                       names=["Period","Grupp","Serie","Värde"])

# Konvertera kolumnerna till rätt datatyp
    trades_df["TradePrice"] = pd.to_numeric(trades_df["TradePrice"], errors='coerce')
    trades_df["IBCommission"] = pd.to_numeric(trades_df["IBCommission"], errors='coerce')
    trades_df["TradeDate"] = pd.to_datetime(trades_df["TradeDate"], errors="coerce")
    valuta_df["Värde"] = pd.to_numeric(valuta_df["Värde"], errors='coerce')
    valuta_df["Period"] = pd.to_datetime(valuta_df["Period"])

# Skapa en tom lista för att lagra de konverterade transaktionerna
    converted_trades = []

# Loop igenom varje rad i Trades.csv
    for index, row in trades_df.iterrows():
        trade_date = row["TradeDate"]
        currency_primary = row["CurrencyPrimary"]
        trade_price = row["TradePrice"]
        ib_commission = row["IBCommission"]

    # Leta upp samma datum och valuta i Valuta.csv
        valuta_row = valuta_df[(valuta_df["Period"] == trade_date) & (valuta_df["Serie"].str.contains(currency_primary))]
    
    # Dubbelkolla att det finns en matchning
        if valuta_row.empty:
            continue
        else:
            exchange_rate = valuta_row.iloc[0]["Värde"]
    
    # Kontrollera att trade_price och ib_commission är numeriska värden
        if pd.isna(trade_price) or pd.isna(ib_commission):
            print(f"TradePrice eller IBCommission är inte numeriska värden för rad {index}.")
            continue
    # Konvertera transaktionen till SEK
        trade_price_sek = trade_price * exchange_rate
        ib_commission_sek = ib_commission * exchange_rate

    # Lägg till transaktionen i den nya listan
        converted_trades.append([row["Symbol"], row["Buy/Sell"], row["Quantity"], trade_price_sek, ib_commission_sek, "SEK", trade_date])

# Skapa en ny DataFrame med de konverterade transaktionerna
        converted_trades_df = pd.DataFrame(converted_trades, columns=["Symbol","Buy/Sell","Quantity","TradePrice","IBCommission","CurrencyPrimary","TradeDate"])

# Skriv ut den konverterade DataFrame

        print(converted_trades_df)
#Spara den konverterade DataFrame till en ny .csv-fil med namnet TradesSEK.csv
        converted_trades_df.to_csv("TradesSEK.csv", index=False)

