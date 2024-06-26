import threading
import serial
import socket
import time
from flask import jsonify


class SensorDataManager:
    def __init__(self, serial_port, baud_rate=9600, udp_port=3000):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.udp_port = udp_port
        self.data_lock = threading.Lock()
        self.sensor_data = {}

    def read_udp_data(self, buffer_size=1024):
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.bind(("", self.udp_port))
            print(f"Starting to listen for UDP data on port {self.udp_port}.")

            while True:
                print("Attempting to read UDP data...")
                try:
                    udp_data, _ = udp_socket.recvfrom(buffer_size)
                    udp_data = udp_data.decode("utf-8").strip()

                    if udp_data:
                        print(f"Received UDP data: {udp_data}")
                        data_dict = self.parse_data(udp_data)

                        with self.data_lock:
                            location = data_dict["sensor_info"]["location"]
                            self.sensor_data[location] = data_dict
                            print(
                                f"Updated sensor_data for {location}: {self.sensor_data}"
                            )

                except Exception as e:
                    print(f"Error reading from udp: {e}")

                time.sleep(60)

        except Exception as e:
            print(f"An error occured: {e}")

    def read_serial_data(self):
        try:
            ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"Starting to read from serial port {self.serial_port}.")

            while True:
                print("Attempting to read serial data...")
                try:
                    serial_data = ser.readline().decode("utf-8").strip()
                    if serial_data:
                        print(f"Received serial data: {serial_data}")
                        data_dict = self.parse_data(serial_data)

                        with self.data_lock:
                            location = data_dict["sensor_info"]["location"]
                            self.sensor_data[location] = data_dict
                            print(
                                f"Updated sensor_data for {location}: {self.sensor_data}"
                            )

                except Exception as e:
                    print(f"Error reading from serial: {e}")

                time.sleep(60)

        except serial.SerialException as e:
            print(f"Serial port error: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def parse_data(self, data):
        data_dict = {
            "sensor_info": {"location": "", "error": False, "status": ""},
            "climate": {"temperature": -1, "humidity": -1},
            "last_updated": "",
        }
        parts = data.split(",")

        for part in parts:
            key, value = part.split(":")
            if key == "error":
                data_dict["sensor_info"]["error"] = bool(int(value))
            elif key == "status":
                data_dict["sensor_info"]["status"] = value
            elif key == "location":
                # TODO: Update the sensors to return the correct location value
                match value:
                    case "Office":
                        data_dict["sensor_info"]["location"] = "Garage"
                    case "Master Bedroom":
                        data_dict["sensor_info"]["location"] = "Office"
                    case _:
                        data_dict["sensor_info"]["location"] = value
            elif key == "temperature":
                data_dict["climate"]["temperature"] = int(float(value))
            elif key == "humidity":
                data_dict["climate"]["humidity"] = int(float(value))

        data_dict["last_updated"] = time.time()
        return data_dict

    def get_data(self):
        with self.data_lock:
            return jsonify(self.sensor_data)
