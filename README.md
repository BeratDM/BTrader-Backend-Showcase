# BTrader Backend Showcase

## This repository showcases some of the classes and systems of my project BTrader

BTrader is a program to create, deploy, and moderate an unlimited number of trade bots to trade on the cryptocurrency market on any coin and any time interval using limitlessly expandable trading strategies. Deployed on a server running 24/7, It has made more than 250 successful trades so far for my personal use and is cleansed of any bugs as far as I've explored.

As for now, I am not comfortable with sharing my full work on the internet as open source. I believe this much of the codebase should be enough to satisfy some of the curiosity of people who want to build a similar project while also showcasing my skills.
While systems in this repository are fully functional, they are only a part of the bigger system and therefore incomplete without it.

The repository contains the following:

- Flask app connecting backend and frontend in `app.py`.
- The bTrader class to handle real-time trading on the market in `btrader.py`. double-layered Asynchronicity and multithreaded architecture.  
- The strategy interface and two strategy implementations with both real-time and backtesting classes.
- Structures of environment variables.

Some of the missing parts in this repository:

- Client connections handling to authorize and trade using a cryptocurrency exchange.
- Bigger structure to moderate multiple traders from the user interface and backend.
- Backtesting.
- Frontend.
- Log handling.
- Market history.
- Serving of the flask app.
- And more.

## You can find the original `Readme.md` below

<br />
<br />
<br />
<br />
<br />
<br />

# BTrader-Extended

## Overview

This project uses Binance API to trade crypto in real-time using technical analysis. It gives the option to backtest the strategies using [backtrader](https://github.com/mementum/backtrader). Any amount of traders can be deployed with any pair/interval/strategy. It also supports the development of new trading strategies (with or without technical analysis).
The Program is running a Flask application with user-friendly UI and has a quick trading option with [lightweight-charts](https://www.tradingview.com/lightweight-charts/) implemented

## Features

1. **Trade With Multiple Trade Bots At The Same Time Using Different Strategies.**

2. **Backtest The Strategies On Whichever Trading Pair and Trade Interval You Want.**

3. **Quick Trade Your Assets On All Trading Pairs.**

4. **Do It All In A User-Friendly Interface.**

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/BeratDM/BinanceTrader-Extended.git
   cd BinanceTrader-Extended
   ```

2. Set up a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Environment Setup:** Create your `.env` file at `./app/.env` with your API keys using `./app/.env.template`.

2. **Run The Program:** Go to the `./app` folder and run `main.py`. Make sure you are using the virtual environment if you set it up. A flask application will start and you can visit the url in your browser.

3. **Strategy Development:** New trading strategies can be developed inside the `app/TradeStrategies/` folder by making a new Python file for your strategy and creating two classes, one for backtesting subclassing the `backtrader.Strategy` class, and the other for live trading subclassing the `bStrategy` class. After that, edit the `app/strategy_manager.py` and your `.env` files similarly to the examples to reference your classes.

---

*Disclaimer: This project is developed for personal purposes. Trading and investing involve significant risks, and using this software does not guarantee any profits. Please conduct thorough testing and research before deploying any trading strategy.*
