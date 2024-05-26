# api.py
import time
import json
from flask import Flask, request, jsonify
from function import setup_mqtt_client, station_data
from interact_blockchain import update_controller_data, get_controller_value


MQTT_TOPIC_PUB = "/innovation/valvecontroller/station"
mqttClient = setup_mqtt_client()
mqttClient.loop_start()

app = Flask(__name__)

def publish_data(station_id):
    if station_id not in station_data:
        return {"error": f"No data available for station_id: {station_id}"}

    data = station_data[station_id]
    # data = {
    #     "station_id": "VALVE_0001",
    #     "station_name": "Van dien tu",
    #     "gps_longitude": 106.89,
    #     "gps_latitude": 10.5,
    #     "sensors": [
    #         {
    #         "sensor_id": "valve_0001",
    #         "sensor_name": "Van nuoc 1",
    #         "sensor_value": 1,
    #         "sensor_unit": ""
    #         },
    #         {
    #         "sensor_id": "valve_0002",
    #         "sensor_name": "Van nuoc 2",
    #         "sensor_value": 0,
    #         "sensor_unit": ""
    #         },
    #         {
    #         "sensor_id": "valve_0003",
    #         "sensor_name": "Van nuoc 3",
    #         "sensor_value": 0,
    #         "sensor_unit": ""
    #         }
    #     ]
    # }
    json_data = json.dumps(data)
    # print(json_data)
    mqttClient.publish(MQTT_TOPIC_PUB, json_data, retain=True)

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
            # add data to blockchain
            # update_controller_data(station_id, sensor_id, 1)
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
            # add data to blockchain
            # receipt = update_controller_data(station_id, sensor_id, 0)
            return jsonify(result), 200

    return jsonify({"error": f"Sensor {sensor_id} not found for station {station_id}"}), 404

@app.route('/get_controller_value', methods=['GET'])
def get_controller_value_api():
    station_id = request.args.get('station_id')
    controller_id = request.args.get('controller_id')
    value = get_controller_value(station_id, controller_id)
    return jsonify({"controller_value": value}), 200


# publish_data(1)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)