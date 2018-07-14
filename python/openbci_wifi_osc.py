import sys;
sys.path.append('.')
from signal import *
import os

# openbci
from openbci import wifi as bci
import logging

# requires python-osc
from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

from threading import Thread
import argparse
# for timestapms
import time
#for ip validation
import socket

if __name__ == '__main__':
    # shield_name = 'OpenBCI-W222'
    # shield_name = 'OpenBCI-5381'
    # shield_name = None
    print ("------------ openbci-wifi osc bridge for supercollider -------------")
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', type=str, default='localhost', help="Host to send OSC messages to.")
    parser.add_argument('-p', '--port', type=int, default=57120, help="Port to send OSC messages to.")
    parser.add_argument('-a', '--address', type=str, default='/obci', help="OSC address for messages sent.")
    parser.add_argument('--log', dest='log', default=False, action='store_true', help="Log program")
    parser.add_argument('--discover', dest='discover', action='store_true', help="Run discovery and quit") #todo add number of attempts and timeout to parameters

    args = parser.parse_args()
    for arg in vars(args):
        print(arg, getattr(args, arg))


    if args.log:
        print ("Logging Enabled: " + str(args.log))
        logging.basicConfig(filename="obci_wifi_osc_%s.log" % (time.strftime("%y%m%d_%H%M%S")), format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
        # logging.basicConfig(filename="obci_wifi_osc.log", format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG)
        logging.info('---------LOG START-------------')
        logging.info(args)
    else:
        print ("Logging Disabled.")

    obci_wifi = None; #global

    #globals for synth init_streaming
    osc_sender_synth = None
    osc_synth_addr = ''
    osc_synth_index = 0
    osc_synth_num_messages = 0

    # addr will be appended to args.address
    def send_main(addr='', *msg):
        print("sending:", msg)
        # osc_sender_main.send_message(args.address + addr, list(msg))
        osc_sender_main.send_message(args.address + addr, msg)

    def send_my_port(addr):
        # print("send_my_port callback, addr:", addr)
        send_main('/receivePort', osc_receiver.server_address[1])

    def start_osc_receiver():
        osc_receiver.serve_forever()

    def stop_osc_receiver():
        osc_server.running = False
        # time.sleep(0.1)
        osc_receiver.close()


    def clean(*args):
        # stop_everything('')
        # print('clean args:', args)
        print("Cleaning OpenBCI bridge: received", args[0])
        # running = False;
        try:
            obci_wifi.disconnect()
            print("WiFi shield disconnnected")
        except:
            print("Error disconnecting WiFi shield")
        try:
            osc_receiver.shutdown()
            print("OSC receiver stopped")
        except:
            pass
        print("Clean! Exiting...")
        # sys.exit(0)
        os._exit(0)


    def discover_shields(unused_addr, timeout=3, attempts=5):
        # print("args:", unused_addr, timeout, attempts )
        obci_wifi = bci.OpenBCIWiFi(log=True, timeout=timeout, ssdp_attempts=attempts, shield_found_cb=lambda ip_address, name, description : send_main('/found', ip_address, name))
        # obci_wifi = bci.OpenBCIWiFi(log=True, timeout=timeout, ssdp_attempts=attempts, shield_found_cb=lambda ip_address, name, description : print("board found!", name))
        # obci_wifi.loop()

    def connect(unused_addr, addressOrName, sample_rate=None, max_packets_to_skip=20, latency=10000, timeout=3, attempts=5):
        # print("args:", unused_addr, timeout, attempts )
        try:
            socket.inet_aton(addressOrName)
            ip = addressOrName
            name = None
        except socket.error:
            ip = None
            name = addressOrName

        global obci_wifi
        try:
            obci_wifi = bci.OpenBCIWiFi(ip_address=ip, shield_name=name, sample_rate=sample_rate, log=True, timeout=timeout, max_packets_to_skip=max_packets_to_skip, latency=latency, high_speed=True, ssdp_attempts=attempts, num_channels=8, shield_found_cb=None)
            # num_channels is ignored

            connected = True
        except:
            connected = False

        osc_sender_main.send_message(args.address + "/connected", connected) # status
        #     # try:
        # obci_wifi.loop()


    def stream_main(sample):
        if sample.accel_data != [0.0, 0.0, 0.0]:
            osc_sender_main.send_message(args.address, [sample.sample_number] + sample.channel_data + sample.accel_data)
        else:
            osc_sender_main.send_message(args.address, [sample.sample_number] + sample.channel_data)


    def prepare_synth_streaming(scHost=None, scPort=None, scMsg='/b_setn', scIndex=0):
        print("obci_wifi.eeg_channels_per_sample:", obci_wifi.eeg_channels_per_sample)
        global osc_sender_synth, osc_synth_addr, osc_synth_index, osc_synth_num_messages
        osc_sender_synth = udp_client.SimpleUDPClient(scHost, scPort)
        osc_synth_addr = scMsg
        osc_synth_index = scIndex
        osc_synth_num_messages = 1 + obci_wifi.eeg_channels_per_sample + 3 # counter, eeg, accelerometer


    def stream_scsynth(sample): # be sure to run prepare_synth_streaming first!
        # print("sample.accel_data:", sample.accel_data)
        # print("sample.sample_number:", sample.sample_number)

        if sample.accel_data != [0.0, 0.0, 0.0]: #is this too heavy?
            osc_sender_synth.send_message(osc_synth_addr, [osc_synth_index, osc_synth_num_messages, sample.sample_number] + sample.channel_data + sample.accel_data)
        else:
            osc_sender_synth.send_message(osc_synth_addr, [osc_synth_index, osc_synth_num_messages, sample.sample_number] + sample.channel_data)


    def start_streaming(addr, scHost=None, scPort=None, scMsg='/b_setn', scIndex=0):
        global obci_wifi
        # if obci_wifi is not None:
        #     obci_wifi.connect() # reconnect
        #     time.sleep(0.5)
        print("Starting streaming...")
        if scHost is None:
            obci_wifi.start_streaming(stream_main)
            # obci_wifi.loop() works better in the main thread, at least allows restarting streaming
            # try:
            #     obci_wifi.loop()
            # except:
            #     print("obci_wifi loop broke")
        else:
            # setup osc sender
            prepare_synth_streaming(scHost, scPort, scMsg, scIndex)
            obci_wifi.start_streaming(stream_scsynth)
            # use different callback with additional parameters?
            pass # for now

    def stop_streaming(addr):
        global obci_wifi
        try:
            obci_wifi.stop() # need to reconnect afterwards?
            # obci_wifi.wifi_write("s")
            # obci_wif.streaming = False
        except:
            print("stopping failed?")
            pass
        # obci_wifi = None # we don't do this anymore, as we can restart streaming now
        # print("obci_wifi after stop:", obci_wifi)


    # def test_signal(addr, sig):
    #     global obci_wifi
    #     obci_wifi.test_signal(sig)

    def wifi_write(addr, char):
        global obci_wifi
        obci_wifi.wifi_write(char)

    # setup client first
    osc_sender_main = udp_client.SimpleUDPClient(args.host, args.port)
    print("Sending OSC messages to %s:%i" % (args.host, args.port))

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/receivePort", send_my_port)
    dispatcher.map("/quit", clean)
    dispatcher.map("/discover", discover_shields)
    dispatcher.map("/connect", connect) #args: addressOrName, sample_rate=None, max_packets_to_skip=20, latency=10000, timeout=3, attempts=5
    dispatcher.map("/start_streaming", start_streaming)
    dispatcher.map("/stop_streaming", stop_streaming)
    # dispatcher.map("/test_signal", test_signal) #doesn't work properly on the OpenBCI_Python side
    dispatcher.map("/send_command", wifi_write)
    dispatcher.map("/send_command", wifi_write)



    osc_receiver = osc_server.ThreadingOSCUDPServer(('0.0.0.0', 0), dispatcher)
    print("Serving on {}".format(osc_receiver.server_address))
    # osc_receiver.serve_forever()
    receiver_thread = Thread(target = start_osc_receiver)
    receiver_thread.daemon = True # will stop on exit
    try:
        receiver_thread.start()
        send_my_port(None)
    except Exception as e:
        raise

    for sig in (SIGINT, SIGTERM):
        signal(sig, clean)


    # running = True

    if args.discover:
        discover_shields('', 5,5)
        clean('unused_arg')
    else:
        pass

    while True:
        # print("running")
        if obci_wifi is not None:
            try:
                obci_wifi.loop()
            except Exception as e:
                print("loop exception")
                time.sleep(1)
        else:
            # print("sleeping")
            time.sleep(1)
