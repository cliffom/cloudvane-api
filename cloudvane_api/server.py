from flask import Flask
from flask_cors import CORS
from sensor_data_manager import SensorDataManager

serial_port = "/dev/ttyACM0"
baud_rate = 9600
udp_port = 3000

app = Flask(__name__)
CORS(app)

sensor_data_manager = SensorDataManager(
    serial_port=serial_port, baud_rate=baud_rate, udp_port=udp_port
)


@app.route("/api/climate", methods=["GET"])
def get_data():
    return sensor_data_manager.get_data()


if __name__ == "__main__":
    from threading import Thread

    serial_thread = Thread(target=sensor_data_manager.read_serial_data, daemon=True)
    udp_thread = Thread(target=sensor_data_manager.read_udp_data, daemon=True)

    serial_thread.start()
    udp_thread.start()

    app.run(host="0.0.0.0", port=8080, debug=False)
