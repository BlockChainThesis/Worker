# api.py
import time
import json
from flask import Flask, request, jsonify
from function import setup_mqtt_client, station_data
from interact_blockchain import get_station_data, add_stations_data, get_number_of_station, get_controller_value


MQTT_TOPIC_PUB = "/innovation/valvecontroller/topic1"
mqttClient = setup_mqtt_client()
mqttClient.loop_start()

app = Flask(__name__)

def publish_data(station_id):
    if station_id not in station_data:
        return {"error": f"No data available for station_id: {station_id}"}

    data = station_data[station_id]
    json_data = json.dumps(data)
    mqttClient.publish(MQTT_TOPIC_PUB, json_data, retain=True)
    # add data to blockchain
    sensorIds = [] 
    sensorValues = []
    sensorUinits = []
    for sensor in data["sensors"]:
        sensorIds.append(sensor["sensor_id"])
        sensorValues.append(str(sensor["sensor_value"]))
        sensorUinits.append(sensor["sensor_unit"])
    receipt = add_stations_data(data["station_id"], data["gps_longitude"], data["gps_latitude"], sensorIds, sensorValues, sensorUinits)
    print("Transaction receipt:", receipt)

    return {"success": True, "message": f"Data published for station_id: {station_id}"}

@app.route('/turn_on', methods=['POST'])
def turn_on():
    station_id = request.json.get('station_id')
    sensor_id = request.json.get('sensor_id')
    if not station_id or not sensor_id:
        return jsonify({"error": "station_id and sensor_id are required"}), 400

    if station_id not in station_data:
        return jsonify({"error": f"No data available for station_id: {station_id}"}), 404

    for sensor in station_data[station_id]['sensors']:
        if sensor['sensor_id'] == sensor_id:
            sensor['sensor_value'] = 1  # Turn on the sensor (example value)
            result = publish_data(station_id)
            return jsonify(result), 200

    return jsonify({"error": f"Sensor {sensor_id} not found for station {station_id}"}), 404

@app.route('/turn_off', methods=['POST'])
def turn_off():
    station_id = request.json.get('station_id')
    sensor_id = request.json.get('sensor_id')
    if not station_id or not sensor_id:
        return jsonify({"error": "station_id and sensor_id are required"}), 400

    if station_id not in station_data:
        return jsonify({"error": f"No data available for station_id: {station_id}"}), 404

    for sensor in station_data[station_id]['sensors']:
        if sensor['sensor_id'] == sensor_id:
            sensor['sensor_value'] = 0  # Turn off the sensor (example value)
            result = publish_data(station_id)
            return jsonify(result), 200

    return jsonify({"error": f"Sensor {sensor_id} not found for station {station_id}"}), 404

@app.route('/get_station_data', methods=['GET'])
def get_station_data_api():
    station_id = request.args.get('station_id')
    if not station_id:
        return jsonify({"error": "station_id is required"}), 400

    data = get_station_data(station_id)
    if not data:
        return jsonify({"error": f"No data available for station_id: {station_id}"}), 404

    return jsonify(data), 200

@app.route('/get_number_of_station', methods=['GET'])
def get_number_of_station_api():
    count = get_number_of_station()
    return jsonify({"number_of_station": count}), 200

@app.route('/get_controller_value', methods=['GET'])
def get_controller_value_api():
    station_id = request.args.get('station_id')
    controller_id = request.args.get('controller_id')
    value = get_controller_value(station_id, controller_id)
    return jsonify({"controller_value": value}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
