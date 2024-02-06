import threading
import serial
import time
from flask import jsonify


class SensorDataManager:
    def __init__(self, serial_port, baud_rate=9600):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.data_lock = threading.Lock()  # Lock for thread-safe operations
        self.sensor_data = {
            "sensor_info": {"location": "default", "error": False},
            "climate": {"temperature": -1, "humidity": -1},
        }

    def read_serial_data(self):
        try:
            ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"Starting to read from serial port {self.serial_port}.")

            while True:
                print("Waiting for serial data...")
                try:
                    serial_data = ser.readline().decode("utf-8").strip()
                    if serial_data:
                        print(f"Received serial data: {serial_data}")
                        data_dict = {
                            "sensor_info": {"location": "", "error": False},
                            "climate": {"temperature": 0, "humidity": 0},
                        }
                        parts = serial_data.split(",")

                        for part in parts:
                            key, value = part.split(":")
                            if key == "error":
                                data_dict["sensor_info"]["error"] = bool(int(value))
                            elif key == "location":
                                data_dict["sensor_info"]["location"] = value
                            elif key == "temperature":
                                data_dict["climate"]["temperature"] = int(float(value))
                            elif key == "humidity":
                                data_dict["climate"]["humidity"] = int(float(value))

                        with self.data_lock:
                            self.sensor_data = data_dict
                            print(f"Updated sensor_data: {self.sensor_data}")

                except Exception as e:
                    print(f"Error reading from serial: {e}")
                time.sleep(60)

        except serial.SerialException as e:
            print(f"Serial port error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_data(self):
        with self.data_lock:
            return jsonify(self.sensor_data)
