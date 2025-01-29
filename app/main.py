from app import app
from waitress import serve
import config
import logging


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(message)s"
)  # This makes the waitress to print out more logs (waitress default log level: WARNING)

if __name__ == "__main__":
    print("Starting Application..")
    portno = config.Flask_Config().DEFAULT_PORT
    should_serve = config.Flask_Config().SHOULD_SERVE

    """
    usedefaultport = input('Do you want to use default port number? [Y][N]\n').lower()
    if usedefaultport != 'y':
        while True:
            customport = input('Port number should be within the valid range.\nPlease enter the port number: ')
            if  0 <= int(customport) < 65535 and customport.isnumeric():
                portno = int(customport)
                break
    """

    if should_serve == False:
        app.run(debug=config.Flask_Config.DEBUG, use_reloader=False, port=portno)  # type: ignore
    else:
        # app.run(host='0.0.0.0')
        serve(app=app, host="0.0.0.0", port=portno)  # type: ignore
