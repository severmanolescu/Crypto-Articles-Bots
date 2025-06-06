# Telegram Bots Documentation
### Overview

This document overviews the Telegram bots running on the Raspberry Pi 4, their features, and planned improvements.

### Current Bots

The project includes 4 bots:
                
+ **Crypto News Bot**
	+ Articles search:
		+  [crypto.news](https://crypto.news/)
		+  [CoinTelegraph](https://cointelegraph.com/)
		+  [Bitcoin Magazine](https://bitcoinmagazine.com/articles)
	+ AI summarizes the articles
	+ Daily statistics
	+ Daily market sentiment
+ **Crypto Market Value Bot**
	+ Market updates for chosen coins
	+ ETH gas fee tracking
	+ Fear and Greed Index
	+ Full portfolio details (P/L, holdings, avg buy price)
	+ Portfolio history plots (P/L, value, total investment)
	+ Coin buy & sell plots
+ **Crypto Alerts Bot**
	+ Price alerts (1h, 24h, 7d, 30d)
+ **Slave Bot**
	+ Details for a specific coin
	+ Show top 10 coins
	+ Compare 2 coins
	+ Convert 2 coins
	+ Market cap change in 24h for a coin
	+ Calculate ROI
	+ Save buy/sell orders
	+ Modify/list the keywords used by the **Crypto News Bot**
	+ Modify / list variables used by the bots

### Planned Features
+ Forex news integration
+ Web dashboard enhancements (please see: https://github.com/severmanolescu/trades_command_center)
+ AI trading bots

### Infrastructure
+ Python 3.12
+ The bots are currently running on a Raspberry PI 4, but they can be used on any device that can run Python 

### Setup & Installation
+ Clone the repository locally 
+ Install dependencies:
	+ `pip install -r requirements.txt` in a Python environment, or
	+ `py -m pip install -r requirements.txt` for console
+ Set up variables, update `/ConfigurationFiles/variables.json`
+ Run the bots:
	+ You can start them one by one
	+ Or use `start_bots.sh` in a Linux environment to start all of them using different screen processes, !! But update BOT_DIR to your directory where your bots are located !!
