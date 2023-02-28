# Write a python script that takes a ulog file as input, imports the sensor_gyro_fifo and sensor_accel_fifo data, unrolls the FIFO data, and writes the unrolled data to a new ulog file.
# The unrolled data is written to a new topic called sensor_gyro_fifo_unrolled and sensor_accel_fifo_unrolled.

from __future__ import print_function

import argparse
import os
import numpy as np

from .core import ULog

#pylint: disable=too-many-locals, invalid-name, consider-using-enumerate

def main():
    """Command line interface"""

    parser = argparse.ArgumentParser(description='Unroll fifo data from ULog to ULog')
    parser.add_argument('filename', metavar='file.ulg', help='ULog input file')

    parser.add_argument('-o', '--output', dest='output', action='store',
                        help='Output directory (default is same as input file)',
                        metavar='DIR')

    args = parser.parse_args()

    if args.output and not os.path.isdir(args.output):
        print('Creating output directory {:}'.format(args.output))
        os.mkdir(args.output)

    unroll_fifo(args.filename, args.output)


def unroll_fifo(ulog_file_name, output):
    """
    Unrolls the fifo data from a ULog file to a new ULog file.

    :param ulog_file_name: The ULog filename to open and read
    :param output: Output file path

    :return: None
    """

    ulog = ULog(ulog_file_name)
    data = ulog.data_list

    output_file_prefix = ulog_file_name + '_unrolled'

    # write to different output path?
    if output:
        base_name = os.path.basename(output_file_prefix)
        output_file_prefix = os.path.join(output, base_name)
    
    # find the number of sensor_gyro_fifo topics
    gyro_fifo_topics = [topic for topic in data if topic.name == 'sensor_gyro_fifo']
    gyro_fifo_count = len(gyro_fifo_topics)

    # find the number of sensor_accel_fifo topics
    accel_fifo_topics = [topic for topic in data if topic.name == 'sensor_accel_fifo']
    accel_fifo_count = len(accel_fifo_topics)

    # unroll the gyro data
    for i in range(gyro_fifo_count):
        gyro_fifo_topic = gyro_fifo_topics[i]
        gyro_fifo_data = gyro_fifo_topic.data

        last_timestamp_sample = gyro_fifo_data.timestamp_sample
        number_of_samples = gyro_fifo_data.samples

        # create a new topic for the unrolled data
        gyro_unrolled_topic = ULog.Data('sensor_gyro_fifo_unrolled', gyro_fifo_topic.multi_id, gyro_fifo_topic.info)

        # loop through the data and unroll it
        for j in number_of_samples:
            for k in range(j):
                gyro_unrolled_topic.add_sample(last_timestamp_sample, gyro_fifo_data.x[k], gyro_fifo_data.y[k], gyro_fifo_data.z[k])
            last_timestamp_sample += 1
