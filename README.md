# BTrader Backend Showcase (February 2024 State)
## Overview

This repository showcases selected components and systems from my BTrader project.

BTrader is an algorithmic trading platform designed to create, deploy, and manage multiple automated trading bots for cryptocurrency markets. It supports trading across all assets and timeframes available through the Binance API. The system is built with a modular strategy architecture, enabling extensible trading logic and independent evaluation of strategies.

The system integrates both live trading and historical backtesting capabilities using Backtrader. It provides a web-based interface with user authentication and includes real-time charting and manual trading functionality powered by Lightweight Charts. [Backtrader](https://github.com/mementum/backtrader) [Lightweight Charts](https://www.tradingview.com/lightweight-charts/)

It has executed 250+ trades during 2024 when deployed on an AWS server for personal use, supporting both high-frequency and longer-term trading strategies.

This repository is intended to provide insight into the architecture and core components for educational and demonstration purposes. Some internal components are intentionally excluded as part of a larger private infrastructure.

## Included Components

- A Flask application (`app.py`) that connects the backend and frontend. Browser cookies containing sensitive data are securely hashed.
- The bTrader class (`btrader.py`) handles real-time market trading. It uses a multithreaded architecture to allow each trader and market calculation to run concurrently, enabling continuous processing of market updates without missing events. This design is useful for computationally expensive evaluations.
- The bStrategy base class for live trading (`bstrategy.py`)
- Two strategy implementations for both live trading and backtesting.
- The bTraderManager class (`btmanager.py`), responsible for managing multiple trader instances.
- Environment variable configurations, later migrated to Doppler for improved security and secret management. [Doppler](https://www.doppler.com/)
- Application serving via `main.py` using Waitress as the production WSGI server. [Waitress](https://github.com/Pylons/waitress)

## Excluded Components

- Client connections for authentication and order processing through the cryptocurrency exchange.
- Trade pair price step adjustments (10<sup>-18</sup> precision) and automatic safety handling for fee-induced position size deviations.
- Backtesting using historical data across any date ranges, trade pairs, intervals, and strategies.
- Frontend implementation.
- Logging system.
- Market history module.
- Other internal systems and newer versions of the architecture with additional upgrades.

## System Architecture Overview
![uml](https://pub-55a8605bd8ee494ab002c0bb70e15fed.r2.dev/github/btrader1101.svg)
## Useful Links
- [binance api docs 1](https://github.com/binance/binance-spot-api-docs)
- [binance api docs 2 (they are different)](https://developers.binance.com/docs/binance-spot-api-docs/README)

---
## Original Project Reference (Legacy)

## Overview

This project uses the Binance API to trade crypto in real-time using market calculations. It also provides the ability to backtest strategies using [Backtrader](https://github.com/mementum/backtrader). Any number of traders can be deployed with various pairs/intervals/strategies. It also supports the development of new trading strategies.
The Program is running a Flask application with a user-friendly UI and has a quick trading option with [lightweight-charts](https://www.tradingview.com/lightweight-charts/) implemented

## Features

1. **Trade With Multiple Trade Bots At The Same Time Using Different Strategies.**

2. **Backtest The Strategies On Whichever Trading Pair and Trade Interval You Want.**

3. **Quick Trade Your Assets On All Trading Pairs.**

4. **Do It All In A User-Friendly Interface.**

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/BeratDM/BTrader-Extended.git
   cd BTrader-Extended
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
