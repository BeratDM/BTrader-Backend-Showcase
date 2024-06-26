//var TRADE_SYMBOL = "LTCUSDT";
//var TRADE_INTERVAL = "1m";
//var BINANCE_USE_TEST_API = false;
/* These variables are now exist in global-scope (in index.html)*/

var chart = LightweightCharts.createChart(document.getElementById("chart"), {
    width: 1000,
    height: 500,
    locale: "tr",
    fontFamily: "-apple-system, BlinkMacSystemFont, Trebuchet MS, Roboto, Ubuntu, sans-serif",
    topColor: 'rgba(21, 146, 230, 0.4)',
    bottomColor: 'rgba(21, 146, 230, 0)',
    lineColor: 'rgba(21, 146, 230, 1)',
    lineStyle: 0,
    lineWidth: 3,
    crosshairMarkerVisible: false,
    crosshairMarkerRadius: 3,

    layout: {
        background: {
            type: 'solid',
            color: "whitesmoke",
        },
        /*textColor: 'rgba(255, 255, 255, 0.9)',
        */

    },
    grid: {
        vertLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
        horzLines: {
            color: 'rgba(197, 203, 206, 0.5)',
        },
    },
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
    },
    rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.8)',
    },
    timeScale: {
        visible: true,
        timeVisible: true,
        secondsVisible: true,

        borderColor: 'rgba(197, 203, 206, 0.8)',
    },

});

var candleSeries = chart.addCandlestickSeries({
    upColor: 'rgba(255, 144, 0, 1)',
    downColor: '#000',
    borderDownColor: 'rgba(255, 144, 0, 1)',
    borderUpColor: 'rgba(255, 144, 0, 1)',
    wickDownColor: 'rgba(255, 144, 0, 1)',
    wickUpColor: 'rgba(255, 144, 0, 1)',
});

/* get history data from flask page*/
// `http://127.0.0.1:5000/history?TRADE_SYMBOL=${TRADE_SYMBOL}&TRADE_INTERVAL=${TRADE_INTERVAL}`
fetch(`${url_history}?TRADE_SYMBOL=${TRADE_SYMBOL}&TRADE_INTERVAL=${TRADE_INTERVAL}`)
    .then((r) => r.json())
    .then((response) => {
        console.log(response)

        candleSeries.setData(response);
    })


/* Get and update chart with real-time values from this websocket */
if (BINANCE_USE_TEST_API == true) {
    var wss_url = "wss://stream.binance.com:9443/ws"
} else {
    var wss_url = "wss://testnet.binance.vision/ws"
}

/* listen to new values realtime using a WebSocket */
var SOCKET = `${wss_url}/${TRADE_SYMBOL.toLowerCase()}@kline_${TRADE_INTERVAL}`
/*console.log(SOCKET)*/
var binanceSocket = new WebSocket(SOCKET)
binanceSocket.onmessage = function (event) {
    var message = JSON.parse(event.data);
    var candlestick = message.k
    candleSeries.update({
        time: candlestick.t / 1000, /* dividing with 1000 to remove milliseconds*/
        open: candlestick.o,
        high: candlestick.h,
        low: candlestick.l,
        close: candlestick.c
    })
}