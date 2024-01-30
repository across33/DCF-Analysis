import bs4 as bs
import requests
import yahoo_fin.stock_info as yf
import json
from sympy import Symbol, solve, Eq
from sympy.parsing.sympy_parser import parse_expr

ICR1 = [8,
        6.5,
        5.5,
        4.25,
        3,
        2.5,
        2.25,
        2,
        1.75,
        1.5,
        1.25,
        0.8,
        0.65,
        0.2,
        0]

ICR2 = [100000,
        8.499999,
        6.499999,
        5.499999,
        4.249999,
        2.999999,
        2.499999,
        2.249999,
        1.999999,
        1.749999,
        1.499999,
        1.249999,
        0.799999,
        0.649999,
        0.199999]
Rating = ['Aaa/AAA',
          'Aa2/AA',
          'A1/A+',
          'A2/A',
          'A3/A-',
          'Baa2/BBB',
          'Ba1/BB+',
          'Ba2/BB',
          'B1/B+',
          'B2/B',
          'B3/B-',
          'Caa/CCC',
          'Ca2/CC',
          'C2/C',
          'D2/D']
Spread = [0.63,
          0.78,
          0.98,
          1.08,
          1.22,
          1.56,
          2.00,
          2.40,
          3.51,
          4.21,
          5.15,
          8.20,
          8.64,
          11.34,
          15.12]
ICR_1 = [12.5,
        9.5,
        7.5,
        6,
        4.5,
        4,
        4,
        3,
        2.5,
        2,
        1.5,
        1.25,
        0.8,
        0.5,
        -100000]
ICR_2 = [100000,
        12.499999,
        9.499999,
        7.499999,
        5.999999,
        4.499999,
        4.499999,
        3.499999,
        2.999999,
        2.499999,
        1.999999,
        1.499999,
        1.249999,
        0.799999,
        0.499999]

Rating_2 = ['Aaa/AAA',
            'Aa2/AA',
            'A1/A+',
            'A2/A',
            'A3/A-',
            'Baa2/BBB',
            'Ba1/BB+',
            'Ba2/BB',
            'B1/B+',
            'B2/B',
            'B3/B-',
            'Caa/CCC',
            'Ca2/CC',
            'C2/C',
            'D2/D']


Spread_2 = [0.63,
            0.78,
            0.98,
            1.08,
            1.22,
            1.56,
            2.00,
            2.40,
            3.51,
            4.21,
            5.15,
            8.20,
            8.64,
            11.34,
            15.12]

Country_Risk_Premium = ['0.48%']
PerpetualGrowthRate = 0.025

def conv_percentage(percentage):
    # if there's a % in string, follow these commands
    if '%' in percentage:
        # strip the % from the analyst estimates,  and put a 1 instead
        percentage_stripped = percentage.replace('%', "", 1)
        return percentage_stripped

def get_sp500_weights():
    # get data from website, parse with beautiful soup
    url = 'https://www.slickcharts.com/sp500'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    resp = requests.get(url, headers=headers)
    soup = bs.BeautifulSoup(resp.text, features="lxml")
    table = soup.find('table', {'class': 'table table-hover table-borderless table-sm'})
    sp500 = {}
    for row in table.findAll('tr')[1:]:
        # grab tcikers, make dictionary key
        sp500_ticker = row.findAll('td')[2].text
        #grab weights, make dictionary value
        sp500_weight = row.findAll('td')[3].text
        # create dictionary key, value pair, add to sp500
        if sp500_ticker == 'BRK.B':
            sp500['BRK-B'] = float(sp500_weight)

        elif sp500_ticker == 'BF.B':
            sp500['BF-B'] = float(sp500_weight)
        elif sp500_ticker == 'NWS':
            pass
        else:
            sp500[sp500_ticker] = float(sp500_weight)
    print(sp500)
    return sp500


# get analyst estimates from yahoo finance for each ticker in the dictionary
def estimates():
    forecast = ()
    sp500_weights = get_sp500_weights()
    print('Type 1 if you would like to refresh the analyst data from yahoo finance\nType 2 if you want to continue with dated data')
    integer = int(input('insert number:'))
    json_forecast = json.dumps(forecast)

    # if user selects 1, refresh the analyst data from yahoo finance and store it in a file as a dictionary
    if integer == 1:
        forecast_dict = {}
        for keys in sp500_weights:
            analyst = yf.get_analysts_info(f'{keys}')
            growth = analyst['Growth Estimates']
            growth_5yr = float(conv_percentage(growth.loc[4][1]))
            print(keys, ':', growth_5yr)
            forecast_dict[keys] = growth_5yr
        with open('forecast_dump.json', 'w') as outfile:
            json.dump(forecast_dict, outfile)

    # otherwise use the data from the current file and multiply the values of the sp500 dictionary and the file dictionary
    else:
        with open('forecast_dump.json') as json_file:
            analyst_data = json.load(json_file)
            estimate_data = {}
            for keys in analyst_data:
                estimate_data[keys] = analyst_data[keys]*sp500_weights[keys]/100
            print(estimate_data)
            for values in estimate_data:
                values = estimate_data.values()
                weighted_forecast = sum(values)
            print(weighted_forecast)
            # Grow FCFE by the calculated growth rate
            year1_FCFE = (249.36 * (1 + (weighted_forecast/100)))
            print(year1_FCFE)
            year2_FCFE = year1_FCFE * (1 + (weighted_forecast/100))
            print(year2_FCFE)
            year3_FCFE = year2_FCFE * (1 + (weighted_forecast/100))
            print(year3_FCFE)
            year4_FCFE = year3_FCFE * (1 + (weighted_forecast/100))
            print(year4_FCFE)
            year5_FCFE = year4_FCFE * (1 + (weighted_forecast/100))
            print(year5_FCFE)
            Recent_Tbond = yf.get_live_price('^TNX')
            Sp500_price = yf.get_live_price('^GSPC')
            print(Sp500_price)


            # Mathematical Expression
            input_string = fr"{year1_FCFE}/(1+x) + {year2_FCFE}/((1+x)**2) + {year3_FCFE}/((1+x)**3) + {year4_FCFE}/((1+x)**4) + {year5_FCFE}/((1+x)**5) + {year5_FCFE}*(1+{Recent_Tbond/100})/((x-{Recent_Tbond/100})*((1+x)**5)) = {Sp500_price} "

            # Creating object of the expression and splitting the expression as LHS and RHS
            x = Symbol('x', real=True)
            lhs = parse_expr(input_string.split('=')[0], local_dict={'x': x})
            rhs = parse_expr(input_string.split('=')[1], local_dict={'x': x})

            # Printing the expression to be evaluated
            print(lhs, "=", rhs)

            #Finding solution using solve function of sympy library
            sol = solve(Eq(lhs, rhs), x)
            solution = sol[0] * 100
            #print(fr"s&p 500 estimated return for the current fiscal year is {solution} %")
            #Calculating an equity risk premium based on the solution output
            equity_risk_premium = solution - Recent_Tbond
            #print(fr'The current equity risk premium based on various estimates is {equity_risk_premium}')
            return equity_risk_premium
ERP = estimates()

def conv_mrktcap(marketcap):
    # if market cap is in trillions, follow these commands
    if 'T' in marketcap:
        # strip the T from the market cap, and put a 1 instead
        marketcap_stripped = marketcap.replace('T', "", 1)
        # Replace the T with 10^12 to convert to integers
        marketcap = float(marketcap_stripped) * (10 ** 12)
    # if market cap is in Billions, follow these commands
    elif 'B' in marketcap:
        # strip the M from the market cap, and put a 1 instead
        marketcap_stripped = marketcap.replace('B', "", 1)
        # Replace the B with 10^12 to convert to integers
        marketcap = float(marketcap_stripped) * (10 ** 9)
    # if market cap is in Millions, follow these commands
    elif 'M' in marketcap:
        marketcap_stripped = marketcap.replace('M', "", 1)
        # Replace the B with 10^12 to convert to integers
        marketcap = float(marketcap_stripped) * (10 ** 6)
    return marketcap

running = True
while running:
    Business_Country = input('What Country is The Business From:')
    Revenue_stream = float(input('What Percentage of Total Revenue Comes From that Country? (1=100%, and if its a developed country write 1):'))
    WAM = int(input('What is the Weighted Average Maturity of Debt Found in 10k Report (if unsure write 5):'))
    print(int(input('Stock Based Compensation:')))
    Ticker = input("Insert Ticker:")
    quote = yf.get_quote_table(Ticker)
    # indexing market cap
    MarketCap = quote["Market Cap"]
    # print market cap
    beta = quote["Beta (5Y Monthly)"]
    print('Market Cap:', "{:,}".format(conv_mrktcap(MarketCap)), '$')
    print('Beta:', beta)
    stats = yf.get_stats_valuation(Ticker)
    Data = yf.get_data(Ticker)
    Balance_Sheet = yf.get_balance_sheet(Ticker)
    financials = yf.get_financials(Ticker)
    analyst = yf.get_analysts_info(Ticker)
    # import company's valuations as stats
    income = yf.get_income_statement(Ticker)
    print(type(stats))
    print(stats)

    Cash = yf.get_cash_flow(Ticker)

    # import comapny's income statement as income
    ebit = income.loc["ebit"]
    # indexing ebit in icnome statement
    ebit2020 = int(ebit["2020"])
    # indexing latest ebit in income statement
    print('Latest Calender Ebit:', "{:,}".format(ebit2020), "$")

    interestExpense = income.loc['interestExpense']
    # indexing interest expense in imcome statement
    interestExpense2020 = int(-interestExpense["2020"])
    # indexing latest interest expemse in income statement
    print('Latest Calendar Interest Expense:', "{:,}".format(interestExpense2020), '$')

    Total_Debt = income.loc['incomeBeforeTax']
    Total_Debt2020 = int(Total_Debt["2020"])
    Tax_Provision = income.loc["incomeTaxExpense"]
    Tax_Provision2020 = int(Tax_Provision["2020"])
    Tax_Rate = (Tax_Provision2020/Total_Debt2020) * 100
    print('Current Year Tax Rate:', '{:.4f}'.format(Tax_Rate), '%')

    #Calculating interest Coverage Ratio (ICR)
    icr = ebit2020 / interestExpense2020
    print("Interest Coverage Ratio:", '{:.4f}'.format(icr))
    # Equity Risk Premium
    print('Country Risk Premium Based Off Business\' Home Country:', (Revenue_stream * Domestic_Business))

    print('Equity Risk Premium:', ERP)

    # live pricing of United States 1O year Treasury Bond
    Tbond = yf.get_data('^TNX')
    Recent_Tbond = yf.get_live_price('^TNX')
    print("10 year Treasury bond:", "{:.4f}".format(Recent_Tbond), '%')

    # Cost of equity for that equity
    Cost_of_Equity = Recent_Tbond + beta * ERP
    print("Cost of Equity:", "{:.4f}".format(Cost_of_Equity), "%")

    stats2 = yf.get_stats(Ticker)
    OutstandingShares = conv_mrktcap(stats2.loc[9][1])
    print('Outstanding Shares:', "{:,}".format(OutstandingShares), 'Shares')
    LivePrice = yf.get_live_price(Ticker)
    MarketValueOfEquity = OutstandingShares * LivePrice
    print('Market Value of Equity', "{:,}".format(round(MarketValueOfEquity)), '$')
    TotalDebt = conv_mrktcap(stats2.loc[44][1])
    print('Total Debt:', "{:,}".format(TotalDebt), '$')

    if conv_mrktcap(MarketCap) > 5000000000:
        # Using for loop to iterate through the list to print out the necessary detail
        for i in range(0, len(ICR1)):
            # Checking if the ICR is in the boundary or not
            if (icr >= ICR1[i] and icr <= ICR2[i]):
                # Printing the results and breaking the loop
                print(f"Equity Rating is {Rating[i]} and Default Spread is {Spread[i]} %")

    elif conv_mrktcap(MarketCap) < 5000000000:
        # Using for loop to iterate through the list to print out the necessary detail
        for i in range(0, len(ICR_1)):
            # Checking if the ICR is in the boundary or not
            if (icr >= ICR_1[i] and icr <= ICR_2[i]):
                # Printing the results and breaking the loop
                print(f"Equity Rating is {Rating_2[i]} and Spread is {Spread_2[i]} %")

                AfterTaxCostofDebt = (((Recent_Tbond/100) + (i/100)) * (1 - (Tax_Rate/100)) *100)
                print('After Tax Cost of Debt:', "{:.2f}".format(AfterTaxCostofDebt), '%')
                CostofDebt = ((Recent_Tbond/100) + (i/100))
                C = interestExpense2020
                Kd = CostofDebt
                T = WAM
                FV = TotalDebt
                MarketValueOfDebt = (C*((1-(1/(1+Kd)**T))/Kd))+(FV/(1+Kd)**T)
                a = MarketValueOfEquity
                b = MarketValueOfDebt
                c = Cost_of_Equity/100
                d = AfterTaxCostofDebt/100
                CostofCapital = c*(a/(a+b)) + d*(b/(b+a))
                print('Cost of Capital (WACC):', "{:.2f}".format(CostofCapital *100), "%")


