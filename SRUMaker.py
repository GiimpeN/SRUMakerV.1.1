import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
import datetime
import time
import os

# Create a file called INFO.SRU and open it in write
def create_info(orgnr, namn, adress, postnr, postort, email):
    with open("INFO.SRU", "w") as file:
        # Write the inputs to the file
        file.writelines("#DATABESKRIVNING_START" + "\n")
        file.writelines("#PRODUKT SRU" + "\n")
        file.writelines("#FILNAMN BLANKETTER.SRU" + "\n")
        file.writelines("#DATABESKRIVNING_SLUT" + "\n")
        file.writelines("#MEDIELEV_START" + "\n")
        file.writelines("#ORGNR " + orgnr + "\n")
        file.writelines("#NAMN " + namn + "\n")
        file.writelines("#ADRESS " + adress + "\n")
        file.writelines("#POSTNR " + postnr + "\n")
        file.writelines("#POSTORT " + postort + "\n")
        file.writelines("#EMAIL " + email + "\n")
        file.writelines("#MEDIELEV_SLUT")


def convert_to_sek(trades_file, valuta_file):
    trades_df = pd.read_csv(trades_file, sep=",", header=0, encoding='utf-8',
                            names=["Symbol", "Buy/Sell", "Quantity", "TradePrice", "IBCommission", "CurrencyPrimary",
                                   "TradeDate"])
    valuta_df = pd.read_csv(valuta_file, sep=";", header=0, encoding='utf-8',
                            names=["Period", "Grupp", "Serie", "Värde"])

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
        valuta_row = valuta_df[
            (valuta_df["Period"] == trade_date) & (valuta_df["Serie"].str.contains(currency_primary))]

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
        converted_trades.append(
            [row["Symbol"], row["Buy/Sell"], row["Quantity"], trade_price_sek, ib_commission_sek, "SEK", trade_date])

        # Skapa en ny DataFrame med de konverterade transaktionerna
        converted_trades_df = pd.DataFrame(converted_trades,
                                           columns=["Symbol", "Buy/Sell", "Quantity", "TradePrice", "IBCommission",
                                                    "CurrencyPrimary", "TradeDate"])


        # Spara den konverterade DataFrame till en ny .csv-fil med namnet TradesSEK.csv
        converted_trades_df.to_csv("TradesSEK.csv", index=False)


def sum_trades():
    # Läs in data till en dataframe
    df = pd.read_csv('TradesSEK.csv')

    # Ändra IBCommission till positivt och gör om till int
    df["IBCommission"] = abs(df["IBCommission"]).astype(int)

    # Gör Quantity till absolutvärde och gör om till int
    df["Quantity"] = abs(df["Quantity"]).astype(int)

    # Räkna ut viktat medelvärde för TradePrice
    df["Weighted_TradePrice"] = df["TradePrice"] * df["Quantity"]
    df["Weighted_Quantity"] = df["Quantity"]
    grouped_df = df.groupby(["Symbol", "Buy/Sell"]).agg({"Symbol":"sum", "Weighted_TradePrice":"sum", "Weighted_Quantity":"sum"})
    grouped_df["Weighted_Avg_TradePrice"] = grouped_df["Weighted_TradePrice"] / grouped_df["Weighted_Quantity"]

    # Summera datan och lägg till viktat medelvärde för TradePrice
    sum_df = df.groupby(["Symbol", "Buy/Sell"]).sum()[["Quantity", "IBCommission"]].join(grouped_df[["Weighted_Avg_TradePrice"]]).reset_index()

    # Gör om Weighted_Avg_TradePrice till int
    sum_df["Weighted_Avg_TradePrice"] = sum_df["Weighted_Avg_TradePrice"].astype(int)

    # Sortera data efter Symbol och Buy/Sell
    sum_df = sum_df.sort_values(by=["Symbol", "Buy/Sell"])
    # Spara ner den summerade data till en csv-fil

    sum_df.to_csv("SumTrades.csv", index=False)


import pandas as pd
import datetime


def convert_sum_trades():
    #reading data from SumTrades.csv
    df = pd.read_csv('SumTrades.csv')

    #reading identification information from INFO.SRU
    with open('INFO.SRU', 'r') as f:
        for line in f:
            if line.startswith('#ORGNR'):
                identification = line.strip()
                break
        else:
            identification = '#ORGNR not found'

    #getting current date and time
    now = datetime.datetime.now()

    #grouping the data by Symbol and Buy/Sell and then performing calculations
    grouped_df = df.groupby(['Symbol','Buy/Sell']).agg({'Buy/Sell':'sum', 'Quantity':'sum', 'IBCommission':'sum', 'Weighted_Avg_TradePrice': 'sum'})

    #calculating the buy amount, sell amount, profit and loss
    grouped_df['Buy_amount'] = grouped_df.apply(lambda row: (row['Weighted_Avg_TradePrice']*row['Quantity']) + (row['IBCommission']*2) if row['Buy/Sell'] == 'BUY' else None, axis=1)
    grouped_df['Sell_amount'] = grouped_df.apply(lambda row: (row['Weighted_Avg_TradePrice']*row['Quantity']) if row['Buy/Sell'] == 'SELL' else None, axis=1)



    grouped_df['Profit'] = grouped_df['Sell_amount'] - grouped_df['Buy_amount']
    grouped_df['Loss'] = grouped_df['Buy_amount'] - grouped_df['Sell_amount']
    grouped_df['Profit'] = grouped_df['Profit'].clip(lower=0)
    grouped_df['Loss'] = grouped_df['Loss'].clip(lower=0)

    grouped_df = grouped_df.groupby('Symbol').agg({'Quantity': 'sum', 'Buy_amount': 'sum', 'Sell_amount': 'sum', 'Profit': 'sum', 'Loss': 'sum'})

    grouped_df['Profit'] = grouped_df['Sell_amount'] - grouped_df['Buy_amount']
    grouped_df['Loss'] = grouped_df['Buy_amount'] - grouped_df['Sell_amount']
    grouped_df['Profit'] = grouped_df['Profit'].clip(lower=0)
    grouped_df['Loss'] = grouped_df['Loss'].clip(lower=0)


    #creating a list of results in the desired format
    final_data = []
    for symbol, values in grouped_df.iterrows():
        year = year_entry.get()
        final_data.append([
            '#BLANKETT K4-{}{}'.format(year, 'P4'),
            '#IDENTITET {} {}'.format(identification.replace("#ORGNR ", ""), now.strftime("%Y%m%d %H%M%S")),
            '#UPPGIFT 3100 {}'.format(int(values['Quantity']/2)),
            '#UPPGIFT 3101 {}'.format(symbol),
            '#UPPGIFT 3102 {}'.format(int(values['Sell_amount'])),
            '#UPPGIFT 3103 {}'.format(int(values['Buy_amount'])),
            '#UPPGIFT 3104 {}'.format(int(values['Profit'])),
            '#UPPGIFT 3105 {}'.format(int(values['Loss'])),
            '#BLANKETTSLUT'
        ])


    #writing the final data to BLANKETTER.SRU
    with open('BLANKETTER.SRU', 'w') as f:
        for row in final_data:
            for line in row:
                f.write(line)
                f.write('\n')
        f.write('#FIL_SLUT')






def select_trades_file():
    global trades_file
    trades_file = filedialog.askopenfilename()
    trades_file_label.config(text=trades_file)

def select_valuta_file():
    global valuta_file
    valuta_file = filedialog.askopenfilename()
    valuta_file_label.config(text=valuta_file)

def main():
    orgnr = orgnr_entry.get()
    namn = namn_entry.get()
    adress = adress_entry.get()
    postnr = postnr_entry.get()
    postort = postort_entry.get()
    email = email_entry.get()

    create_info(orgnr, namn, adress, postnr, postort, email)
    time.sleep(2)
    convert_to_sek(trades_file, valuta_file)
    time.sleep(2)
    sum_trades()
    time.sleep(2)
    convert_sum_trades()

    # Ta bort filerna efter att alla operationer är klara
    os.remove("SumTrades.csv")
    os.remove("TradesSEK.csv")
    
    messagebox.showinfo("Success", "INFO.SRU & BLANKETTER.SRU Skapades")

root = tk.Tk()
root.title("SRUMaker")

trades_file_label = tk.Label(root, text="Ingen fil vald")
trades_file_label.grid(row=0, column=0)

select_trades_button = tk.Button(root, text="Välj Trades-fil", command=select_trades_file)
select_trades_button.grid(row=0, column=1)

valuta_file_label = tk.Label(root, text="Ingen fil vald")
valuta_file_label.grid(row=1, column=0)

select_valuta_button = tk.Button(root, text="Välj Valuta-fil", command=select_valuta_file)
select_valuta_button.grid(row=1, column=1)

# Skapa textfält för alla inputs
orgnr_label = tk.Label(root, text="ORGNR/PERSONNR: ")
orgnr_label.grid(row=2, column=0)

orgnr_entry = tk.Entry(root)
orgnr_entry.grid(row=2, column=1)

namn_label = tk.Label(root, text="NAMN: ")
namn_label.grid(row=3, column=0)

namn_entry = tk.Entry(root)
namn_entry.grid(row=3, column=1)

adress_label = tk.Label(root, text="ADRESS: ")
adress_label.grid(row=4, column=0)

adress_entry = tk.Entry(root)
adress_entry.grid(row=4, column=1)

postnr_label = tk.Label(root, text="POSTNR: ")
postnr_label.grid(row=5, column=0)

postnr_entry = tk.Entry(root)
postnr_entry.grid(row=5, column=1)

postort_label = tk.Label(root, text="POSTORT: ")
postort_label.grid(row=6, column=0)

postort_entry = tk.Entry(root)
postort_entry.grid(row=6, column=1)

email_label = tk.Label(root, text="EMAIL: ")
email_label.grid(row=7, column=0)

email_entry = tk.Entry(root)
email_entry.grid(row=7, column=1)

year_label = tk.Label(root, text="Vilket år gäller deklarationen?: ")
year_label.grid(row=8, column=0)

year_entry = tk.Entry(root)
year_entry.grid(row=8, column=1)




# Skapa en knapp för att köra alla koderna
run_button = tk.Button(root, text="Kör", command=main)
run_button.grid(row=9, column=0, columnspan=2, pady=10)

root.mainloop()
