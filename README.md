# BTrader Backend Showcase as of February 2024 State

## This repository showcases some of the classes and systems of my project BTrader

BTrader is a program that creates, deploys, and moderates an unlimited number of trade bots to trade in the cryptocurrency market on any coin and at any time interval using limitlessly expandable trading strategies. Deployed on an AWS server running 24/7, It has made more than 250 successful trades in 2024 for my personal use and is cleansed of any bugs as far as I've explored.

As for now, I will not be sharing the full project as open source. I believe this much of the codebase should be enough to satisfy some of the curiosity of people who want to build a similar project and guide them while also showcasing my skills.
While systems in this repository are fully functional, they are meant to be used with other systems therefore might be incomplete without.

The repository contains the following:

- Flask app connecting the backend to frontend in `app.py`.
- The bTrader class to handle real-time trading on the market in `btrader.py`. Asynchronicity and multithreaded architecture.  
- The strategy interface and two strategy implementations with both real-time and backtesting classes.
- bTraderManager class to handle multiple traders in `btmanager.py`
- Structures of environment variables.

Some of the missing parts in this repository:

- Client connections for authorization handling and order processing through the cryptocurrency exchange.
- Trade pair price step adjustments(10<sup>-18</sup> precision), auto order safety for up to %10 account balance deficit.
- Backtesting with historical data using any date-span, trade pair, interval, strategy.
- Frontend.
- Log handling.
- Market history.
- etc.

<br />
<br />
<br />

## Relations
![uml](https://cdn.discordapp.com/attachments/715073056607043605/1333924491289563166/btrader1101.svg?ex=679aa97d&is=679957fd&hm=6f62b08cfa60b19dc22361c07c2a60b2e9be3c03b22efd76078b39c0e4efe18d&)

## You can find the original `Readme.md` below

<br />
<br />
<br />
<br />
<br />
<br />

---

# BTrader-Extended

## Overview

This project uses Binance API to trade crypto in real-time using technical analysis. And gives the option to backtest the strategies using [backtrader](https://github.com/mementum/backtrader). Any amount of traders can be deployed with any pair/interval/strategy. It also supports the development of new trading strategies.
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
