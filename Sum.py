import pandas as pd

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
    print(sum_df)
    sum_df.to_csv("SumTrades.csv", index=False)
