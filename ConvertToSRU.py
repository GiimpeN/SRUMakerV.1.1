import pandas as pd
import datetime

import os

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

    #grouping the data by symbol and then performing calculations
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

    #aggregating the data by symbol



    #creating a list of results in the desired format
    final_data = []
    for symbol, values in grouped_df.iterrows():
        import SRUMaker
        year = GUI.year_entry.get()
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


