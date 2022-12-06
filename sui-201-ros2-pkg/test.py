#! /usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
import  serial
import math
from std_msgs.msg import Float64    
from geometry_msgs.msg import PointStamped

def DueData(inputdata):  
    CheckSum = 0
    for i in range(0,22):
        CheckSum += inputdata[i] # Add up data.
    if inputdata[22] == (CheckSum & 0xff): # Stop if checksum is wrong.
        meaVoltage = int.from_bytes(inputdata[6:10], "big") / 1000.0 # V
        meaCurrent = int.from_bytes(inputdata[10:14], "big") / 1000.0 # A
        meaPower   = int.from_bytes(inputdata[14:18], "big") /1000.0 # W
        meaPowerUsage = int.from_bytes(inputdata[18:22], "big") /10000.0 # Wh
        pub_Voltage(meaVoltage)
        pub_Power(meaCurrent,meaPower,meaPowerUsage)


def pub_Voltage(meaVoltage):
    pub_vol = Float64()
    pub_vol.data = meaVoltage
    pubVoltage.publish(pub_vol)


def pub_Power(meaCurrent,meaPower,meaPowerUsage):
    pub_measure = PointStamped()
    pub_measure.header.frame_id = 'Unit(X: A, Y: W, Z: Wh)'
    pub_measure.header.stamp = node.get_clock().now().to_msg()
    pub_measure.point.x = meaCurrent
    pub_measure.point.y = meaPower
    pub_measure.point.z = meaPowerUsage
    pubPower.publish(pub_measure)


if __name__ == '__main__':
    # set Node name 
    node_name = 'SUI_201_Power_Unit'

    # 
    port = '/dev/power'
    # port = '/dev/ttyUSB0'
    
    # set Baudrate
    baud = 115200

    
    ser = serial.Serial(port, baud, timeout=0.5)

    rclpy.init()
    node = rclpy.create_node(node_name)
    rate = node.create_rate(20) # max feedback speed
    pubPower = node.create_publisher(
        PointStamped, 'power_comsume', qos_profile=qos_profile_sensor_data)
    pubVoltage = node.create_publisher(
        Float64, 'battery_voltage', qos_profile=qos_profile_sensor_data)

    powerQuery = b'\x55\x55\x01\x01\x00\x00\xAC' # Query Full state
    try:
        while rclpy.ok():
            ser.write(powerQuery)
            datahex = ser.read(23)
            DueData(datahex)
            rate.sleep()
    except KeyboardInterrupt:
        print("Node Shutdown")