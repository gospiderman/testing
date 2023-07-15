#/opt/homebrew/bin/python3.8

# Prerequisites:
# 1. Install Paramiko on the host machine
# 2. Change all relevant paths
# 3. Ensure that Device under test shows up in the usb network + host machine is configured as 192.168.1.*


import sys
import paramiko
import time
import vlc
import glob
import os
from subprocess import *
import wave
import contextlib
import math
import csv
import datetime
from pandas import *


def get_duration(path_to_audio_file):
    with contextlib.closing(wave.open(path_to_audio_file, 'r')) as f:
        frames = f.getnframes()
        duration = frames / float(rate)
        rate = f.getframerate()
        return duration

# Dataset
dataset1_path = '/Users/Documents/automation/Dataset/DogBarking/'
dataset2_path = '/Users/Documents/automation/Dataset/CarAlarm/'
dataset3_path = '/Users/Documents/automation/Dataset/GlassBreaking/'

playlist = glob.glob(dataset1_path + '*.wav', recursive=True)

# If audio files name in dataset1_path consist with whitespace and/or comas - replacing it to underscore so the script can run without fail
result = [os.rename(os.path.join(dataset1_path, f), os.path.join(dataset1_path, f).replace(' ', '_')) for f in os.listdir(dataset1_path)]
result = [os.rename(os.path.join(dataset1_path, f), os.path.join(dataset1_path, f).replace(',', '_')) for f in os.listdir(dataset1_path)]

# Folder to save result logs
output_folder1 = '/Users/Documents/automation/Results/ResultsDogBarking/'
output_folder2 = '/Users/Documents/automation/Results/ResultsCarAlarm/'
output_folder3 = '/Users/Documents/automation/Results/ResultsGlassBreaking/'

# File to log timestamps of tracks played
csv_logfile_name = output_folder1 + 'playback_log.csv'

# Write headers to logfile for timestamp
with open(csv_logfile_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Serial_No", "Track_Name", "Start Time Stamp", "End Time Stamp"])
        
# SSH parameters
host_ip = "192.168.1.121"
username = "root"
password = ""
client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the device
client.connect(host_ip, username=username, password=password)
print('Device Connected')

# Commands
command_aed_detection_results_remove = "rm /var/aed/events_dump.txt"
command_aed_detection_results_copy = "scp " + "root@" + host_ip + ":/var/aed/events_dump.txt " + output_folder1

# Stop any previously running AED pipes
print('Stopping any previous instance AED pipeline')
stdin, stdout, stderr = client.exec_command(command_aed_stop)
time.sleep(2)

# Initializing VLC instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

########################
# Playback of DATASET_1
########################

print('\n********************************************************************************')
print('\nStarting loop with all audio files in ' + dataset1_path + '\n')
print('--------------------------------------------------------------------------------')

# Counter for number of tracks played
number_of_tracks = 0

for song in playlist:
    print("Path to track: " + song)
    TempList = song.split('/')
    track_name = TempList[len(TempList) - 1]
    print("Track name: " + track_name)

    number_of_tracks += 1

    # Make sure old temp file has been deleted
    os.system("rm temp.wav 2> /dev/null")
    # Make a copy before playing using VLC to avoid error due to long filename
    os.system("cp " + song + " temp.wav")
    media = vlc_instance.media_new("temp.wav")
    player.set_media(media)

    # Start AED pipe -> wait 10s -> start playback -> after plyaback is comp, wait 10s -> stop AED pipe
    t_start_process = datetime.datetime.now()
    print(t_start_process, ': Start AED pipe')
    stdin, stdout, stderr = client.exec_command(command_aed_start)

    # Keep a gap between each playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Save start time stamp and start playback
    t_start = datetime.datetime.now()
    print(t_start, ': Start playing audio track through the speaker')
    player.play()

    # Either sleep for durtaion of the playback
    # time.sleep(duration)
    # OR
    # pool to check player state to know whether playback has ended
    Ended = 6
    current_state = player.get_state()
    while current_state != Ended:
        current_state = player.get_state()

    # Save end time stamp
    t_end = datetime.datetime.now()
    print(t_end, ': End of track')

    # Wait 10s at the end of playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Stop Pipeline
    stdin, stdout, stderr = client.exec_command(command_aed_stop)
    t_stop_process = datetime.datetime.now()
    print(t_stop_process, ': Stop AED pipe')
    time.sleep(3)

    # Copy detetcion results
    os.system(command_aed_detection_results_copy)

    # Rename to track name
    command_aed_detection_results_rename = "mv " + output_folder1 + "events_dump.txt " + output_folder1 + \
                                           os.path.splitext(track_name)[0] + ".txt"
    os.system(command_aed_detection_results_rename)

    # Remove files from device
    stdin, stdout, stderr = client.exec_command(command_aed_detection_results_remove)

    # Remove temp file
    os.system("rm temp.wav")

    # Order in which data is saved in timestamp_logfile
    newRow = [number_of_tracks, track_name, t_start, t_end]

    # Write data to logfile
    with open(csv_logfile_name, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(newRow)

    print('Number of files done : ', number_of_tracks)
    print('--------------------------------------------------------------------------------')

    time.sleep(10)

print('Total Number of files for the first Dataset1 done : ', number_of_tracks)
print('1/3 of script is complete')
print('Starting next part of the script...')
print('********************************************************************************')

###########################
# Playback of DATASET_2
###########################

playlist = glob.glob(dataset2_path + '*.wav', recursive=True)

# If audio files name in dataset2_path consist with whitespace and/or comas - replacing it to underscore so the script can run without fail
result = [os.rename(os.path.join(dataset2_path, f), os.path.join(dataset2_path, f).replace(' ', '_')) for f in os.listdir(dataset2_path)]
result = [os.rename(os.path.join(dataset2_path, f), os.path.join(dataset2_path, f).replace(',', '_')) for f in os.listdir(dataset2_path)]


# File to log timestamps of tracks played
csv_logfile_name = output_folder2 + 'playback_log.csv'

# Write headers to logfile for timestamp
with open(csv_logfile_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Serial_No", "Track_Name", "Start Time Stamp", "End Time Stamp"])

# Commands
command_aed_detection_results_copy = "scp " + "root@" + host_ip + ":/var/aed/events_dump.txt " + output_folder2

# Stop any previously running AED pipes
print('Stopping any previous instance AED pipeline')
stdin, stdout, stderr = client.exec_command(command_aed_stop)
time.sleep(2)

# Initializing VLC instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

print('\n********************************************************************************')
print('\nStarting loop with all audio files in ' + dataset2_path + '\n')
print('--------------------------------------------------------------------------------')

# Counter for number of tracks played
number_of_tracks = 0

for song in playlist:
    print("Path to track: " + song)
    TempList = song.split('/')
    track_name = TempList[len(TempList) - 1]
    print("Track name: " + track_name)

    number_of_tracks += 1

    # Make sure old temp file has been deleted
    os.system("rm temp.wav 2> /dev/null")
    # Make a copy before playing using VLC to avoid error due to long filename
    os.system("cp " + song + " temp.wav")
    media = vlc_instance.media_new("temp.wav")
    player.set_media(media)

    # Start AED pipe -> wait 10s -> start playback -> after plyaback is comp, wait 10s -> stop AED pipe
    t_start_process = datetime.datetime.now()
    print(t_start_process, ': Start AED pipe')
    stdin, stdout, stderr = client.exec_command(command_aed_start)

    # Keep a gap between each playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Save start time stamp and start playback
    t_start = datetime.datetime.now()
    print(t_start, ': Start playing audio track through the speaker')
    player.play()

    # OR

    # pool to check player state to know whether playback has ended
    Ended = 6
    current_state = player.get_state()
    while current_state != Ended:
        current_state = player.get_state()

    # Save end time stamp
    t_end = datetime.datetime.now()
    print(t_end, ': End of track')

    # Wait 10s at the end of playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Stop Pipeline
    stdin, stdout, stderr = client.exec_command(command_aed_stop)
    t_stop_process = datetime.datetime.now()
    print(t_stop_process, ': Stop AED pipe')
    time.sleep(3)

    # Copy detetcion results
    os.system(command_aed_detection_results_copy)

    # Rename to track name
    command_aed_detection_results_rename = "mv " + output_folder2 + "events_dump.txt " + output_folder2 + \
                                           os.path.splitext(track_name)[0] + ".txt"
    os.system(command_aed_detection_results_rename)

    # Remove files from device
    stdin, stdout, stderr = client.exec_command(command_aed_detection_results_remove)

    # Remove temp file
    os.system("rm temp.wav")

    # Order in which data is saved in timestamp_logfile
    newRow = [number_of_tracks, track_name, t_start, t_end]

    # Write data to logfile
    with open(csv_logfile_name, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(newRow)

    print('Number of files done : ', number_of_tracks)
    print('--------------------------------------------------------------------------------')

    time.sleep(10)

print('Total Number of files for the second Dataset2 done : ', number_of_tracks)
print('2/3 of script is complete')
print('Starting next part of the script...')
print('********************************************************************************')

#########################
# Playback of DATASET_3
#########################

playlist = glob.glob(dataset3_path + '*.wav', recursive=True)

# If audio files name in dataset3_path consist with whitespace and/or comas - replacing it to underscore so the script can run without fail
result = [os.rename(os.path.join(dataset3_path, f), os.path.join(dataset3_path, f).replace(' ', '_')) for f in os.listdir(dataset3_path)]
result = [os.rename(os.path.join(dataset3_path, f), os.path.join(dataset3_path, f).replace(',', '_')) for f in os.listdir(dataset3_path)]


# File to log timestamps of tracks played
csv_logfile_name = output_folder3 + 'playback_log.csv'

# Write headers to logfile for timestamp
with open(csv_logfile_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Serial_No", "Track_Name", "Start Time Stamp", "End Time Stamp"])

# Commands
command_aed_detection_results_copy = "scp " + "root@" + host_ip + ":/var/aed/events_dump.txt " + output_folder3


# Stop any previously running AED pipes
print('Stopping any previous instance AED pipeline')
stdin, stdout, stderr = client.exec_command(command_aed_stop)
time.sleep(2)

# Initializing VLC instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

print('\n********************************************************************************')
print('\nStarting loop with all audio files in ' + dataset3_path + '\n')
print('--------------------------------------------------------------------------------')

# Counter for number of tracks played
number_of_tracks = 0

for song in playlist:
    print("Path to track: " + song)
    TempList = song.split('/')
    track_name = TempList[len(TempList) - 1]
    print("Track name: " + track_name)

    number_of_tracks += 1

    # Make sure old temp file has been deleted
    os.system("rm temp.wav 2> /dev/null")
    # Make a copy before playing using VLC to avoid error due to long filename
    os.system("cp " + song + " temp.wav")
    media = vlc_instance.media_new("temp.wav")
    player.set_media(media)

    # Start AED pipe -> wait 10s -> start playback -> after plyaback is comp, wait 10s -> stop AED pipe
    # Start AED Pipeline
    t_start_process = datetime.datetime.now()
    print(t_start_process, ': Start AED pipe')
    stdin, stdout, stderr = client.exec_command(command_aed_start)

    # Keep a gap between each playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Save start time stamp and start playback
    t_start = datetime.datetime.now()
    print(t_start, ': Start playing audio track through the speaker')
    player.play()

    # OR
    # pool to check player state to know whether playback has ended
    Ended = 6
    current_state = player.get_state()
    while current_state != Ended:
        current_state = player.get_state()

    # Save end time stamp
    t_end = datetime.datetime.now()
    print(t_end, ': End of track')

    # Wait 10s at the end of playback
    print('Waiting 10 secs...')
    time.sleep(10)

    # Stop Pipeline
    stdin, stdout, stderr = client.exec_command(command_aed_stop)
    t_stop_process = datetime.datetime.now()
    print(t_stop_process, ': Stop AED pipe')
    time.sleep(3)

    # Copy detetcion results
    os.system(command_aed_detection_results_copy)

    # Rename to track name
    command_aed_detection_results_rename = "mv " + output_folder3 + "events_dump.txt " + output_folder3 + \
                                           os.path.splitext(track_name)[0] + ".txt"
    os.system(command_aed_detection_results_rename)

    # Remove files from device
    stdin, stdout, stderr = client.exec_command(command_aed_detection_results_remove)

    # Remove temp file
    os.system("rm temp.wav")

    # Order in which data is saved in timestamp_logfile
    newRow = [number_of_tracks, track_name, t_start, t_end]

    # Write data to logfile
    with open(csv_logfile_name, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(newRow)

    print('Number of files done : ', number_of_tracks)
    print('----------------------------------------------------------------------------')

    time.sleep(10)

print('\nEnd of loop!')

# Close the client
client.close()
stdin.close()

print('Total Number of files for the Dataset3 done : ', number_of_tracks)
print('3/3 of script is complete!')
print('Goodbye')
print('********************************************************************************')

###################################################################################################