<div id="top"></div>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1> Algoritmisk handel med långsiktiga investeringsstrategier </h1>
</div>





## Utveckling av en investeringsrobot med konkret implementatio av koncepten pair trading och Fibonacci retracements

Detta system är en investeringsrobot som implementerat pair trading och Fibonacci retracements.
Pairs trading är en algoritms som är marknadsneutral med målet att alltid ha positiv avkassning medans Fibonacci retracements är utformad för att generera högre 

Utvecklingen av denna robot skedde som ett kandidatarbete på Chalmers Tekniska Högskola med Institutionen för data- och informationsteknik samt handledaren Arne Linde.


<p align="right">(<a href="#top">Tillbaka till toppen</a>)</p>



### Byggt med

* [Python](https://www.python.org/)
* [PostgreSQL](https://www.postgresql.org/)
* [Backtrader](https://www.backtrader.com/)
* [Alpaca](https://alpaca.markets/)
* [YLiveTicker](https://github.com/yahoofinancelive/yliveticker/)
* [Yahoo! Finance API](https://github.com/ranaroussi/yfinance)

<p align="right">(<a href="#top">Tillbaka till toppen</a>)</p>



<!-- GETTING STARTED -->
## Starta programmet

### Nödvändig förutsättning

Detta är ett exempel på hur du installerar bibliotek
* pip
  ```sh
  pip install "paketnamn"
  ```
* Skapa ett Alpaca konto och hämta API nycklar på [https://alpaca.markets/](https://alpaca.markets/)

### Installation


1. Klona repot
   ```sh
   git clone https://github.com/AliAlladin/TradingBot-DATX02-VT22.git
   ```
2. Navigera in till filvägen som den klonade koden ligger på

3. Installera PIP paketen
   ```sh
   pip install -r requirements.txt
   ```
4. Lägg till dina API nycklar i en fil under Alpaca mappen och namge den `config.py`
   ```py
   BASE_URL = 'https://paper-api.alpaca.markets'
   ALPACA_API_KEY = 'NYCKELN'
   ALPACA_SECRET_KEY = 'HEMLIGA NYCKELN'
   data_url = 'wss://data.alpaca.markets'
   ```

5. Ladda in CSV-filer med historisk aktiedata från First Rate Data LLC som är konverterade från TXT till CSV. 

6. Ladda in en CSV-fil med historisk data för aktier som ska handlas i real tid i följande format:
<img src="https://i.imgur.com/I4bdHyA.png" width="750" height="500">

<p align="right">(<a href="#top">Tillbaka till toppen</a>)</p>



<!-- USAGE EXAMPLES -->
## Användning

Starta programmet genom att köra:
Pairs Trading:
```sh
python3 main.py
```
eller
Fibonacci retracements
```sh
python3 mainFib.py
```

<p align="right">(<a href="#top">Tillbaka till toppen</a>)</p>


## Utvecklare

* [Artin Abiri](https://github.com/ArtinAbiri)
* [Ali Alladin](https://github.com/AliAlladin)
* [Oskar Hellsén Palmqvist](https://github.com/OskarHP1)
* [Lenia Malki](https://github.com/LeniaMalki)
* [Isak Nilsson](https://github.com/Isak15)
* [Samuel Winqvist](https://github.com/samwin123)
