"""
Core OpenBCI object for handling connections and samples from the WiFi Shield
Note that the LIB will take care on its own to print incoming ASCII messages if any (FIXME, BTW).
EXAMPLE USE:
def handle_sample(sample):
  print(sample.channels_data)
wifi = OpenBCIWifi()
wifi.start(handle_sample)
TODO: Cyton/Ganglion JSON
TODO: Ganglion Raw
TODO: Cyton Raw
"""
import asyncore
import atexit
import json
import logging
import re
import socket
import timeit
import netifaces
import ipaddress
try:
    import urllib2
except ImportError:
    import urllib

import requests
import xmltodict

from openbci.utils import k, ParseRaw, OpenBCISample, ssdp

SAMPLE_RATE = 0  # Hz

'''
#Commands for in SDK
command_stop = "s";
command_startBinary = "b";
'''


class OpenBCIWiFi(object):
    """
    Handle a connection to an OpenBCI wifi shield.
    Args:
      ip_address: The IP address of the WiFi Shield, "None" to attempt auto-detect.
      shield_name: The unique name of the WiFi Shield, such as `OpenBCI-2AD4`, will use SSDP to get IP address still,
        if `shield_name` is "None" and `ip_address` is "None", will connect to the first WiFi Shield found using SSDP
      sample_rate: The sample rate to set the attached board to. If the sample rate picked is not a sample rate the attached
        board can support, i.e. you send 300 to Cyton, then error will be thrown.
      log:
      timeout: in seconds, disconnect / reconnect after a period without new data -- should be high if impedance check
      max_packets_to_skip: will try to disconnect / reconnect after too many packets are skipped
    """

    def __init__(self, ip_address=None, shield_name=None, sample_rate=None, log=True, timeout=3,
                 max_packets_to_skip=20, latency=10000, high_speed=True, ssdp_attempts=5,
                 num_channels=8, shield_found_cb=None, useTCP=True): #shield_found_cb overrides automatically connecting to the found shield; it is passed (ip_address, shield_name, device_description);
        # these one are used
        self.daisy = False
        self.high_speed = high_speed
        self.impedance = False
        self.ip_address = ip_address
        self.latency = latency
        self.log = log  # print_incoming_text needs log
        self.max_packets_to_skip = max_packets_to_skip
        self.num_channles = num_channels
        self.sample_rate = sample_rate
        self.shield_name = shield_name
        self.ssdp_attempts = ssdp_attempts
        self.streaming = False
        self.timeout = timeout
        self.in_discovery = False
        self.useTCP = useTCP

        # might be handy to know API
        self.board_type = "none"
        # number of EEG channels
        self.eeg_channels_per_sample = 0
        self.read_state = 0
        self.log_packet_count = 0
        self.packets_dropped = 0
        self.time_last_packet = 0

        if self.log:
            print("Welcome to OpenBCI Native WiFi Shield Driver - Please contribute code!")

        # get all local addresses (ipv4, ipv6, suppressLoopback)
        self.local_ip_addresses = self._get_local_ip_addresses(True, False, True)

        # wifi server is not created until after finding the shield
        # self.local_wifi_server = WiFiShieldServer(self.local_ip_addresses[0], 0) #first address for now
        # self.local_wifi_server_port = self.local_wifi_server.socket.getsockname()[1]
        self.local_wifi_server = None # until we find/connect to a shield

        if ip_address is None:
            if self.shield_name is None:
                print("Trying to find all WiFi shields on your local wireless network")
            else:
                print("Trying to find %s WiFi shield on your local wireless network" % (self.shield_name))
            for i in range(ssdp_attempts):
                self.in_discovery = True
                try:
                    if shield_found_cb is not None:
                        this_cb = shield_found_cb
                    else:
                        this_cb = self.on_shield_found
                    self.find_wifi_shield(shield_name=self.shield_name, wifi_shield_cb=this_cb)
                    # self.find_wifi_shield(shield_name=self.shield_name)
                    if not self.in_discovery:
                        print("finishing discovery")
                        break
                except OSError:
                    # Try again
                    if i >= (ssdp_attempts - 1) and self.log: #only log at the end
                        print("Did not find matching WiFi Shields")
        else:
            self.on_shield_found(ip_address, shield_name, '')

    def on_shield_found(self, ip_address, name, description):
        self.in_discovery = False
        self.local_ip_address = self._get_local_ip_address(ip_address)
        # Intentionally bind to port 0
        self.local_wifi_server = WiFiShieldServer(self.local_ip_address, 0, useTCP=self.useTCP)
        self.local_wifi_server_port = self.local_wifi_server.socket.getsockname()[1]
        if self.log:
            print("Opened socket on %s:%d" % (self.local_ip_address, self.local_wifi_server_port))

        self.ip_address = ip_address
        self.connect()
        # Disconnects from board when terminated
        atexit.register(self.disconnect)

    def loop(self):
        asyncore.loop()

    def _get_local_ip_address(self, addr):
        """
        Gets the local ip address of this computer
        @returns str Local IP address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((addr, 80))
        local_ip_address = s.getsockname()[0]
        s.close()
        return local_ip_address

    def _get_local_ip_addresses(self, ipv4=True, ipv6=False, suppressLoopback=True):
        """
        Get all local ip addresses of this computers
        @returns a list of str
        """
        allIPs = []
        for iface in netifaces.interfaces():
            ifaddrs = netifaces.ifaddresses(iface)
            if(ipv4):
                if netifaces.AF_INET in ifaddrs:
                    for ifaddr in ifaddrs[netifaces.AF_INET]:
                        if 'addr' in ifaddr:
                            thisAddr = ifaddr['addr']
                            if not ipaddress.ip_address(thisAddr).is_loopback or not suppressLoopback:
                                allIPs.append(thisAddr)
            if(ipv6):
                if netifaces.AF_INET6 in ifaddrs:
                    for ifaddr in ifaddrs[netifaces.AF_INET6]:
                        if 'addr' in ifaddr:
                            #add v6 but remove stuff like %eth0 that gets thrown on end of some addrs
                            thisAddr = ifaddr['addr'].split('%')[0]
                            if not ipaddress.ip_address(thisAddr).is_loopback or not suppressLoopback:
                                allIPs.append(thisAddr)
        return allIPs

    # scans available interfaces and chooses the local IP address on the same network as addr
    # def _get_matching_local_ip_address(self, addr=None):
    #     """
    #     Get matching ip to bind to (on the same network)
    #     @returns a list of str
    #     """
    #     allIPs = []
    #     for iface in netifaces.interfaces():
    #         ifaddrs = netifaces.ifaddresses(iface)
    #
    #         if netifaces.AF_INET in ifaddrs:
    #             for ifaddr in ifaddrs[netifaces.AF_INET]:
    #                 if 'addr' in ifaddr:
    #                     thisAddr = ifaddr['addr']
    #                     thisMask = ifaddr['netmask']
    #                     if ipaddress.ip_address(addr) in ipaddress.ip_network((thisAddr, thisMask), False):
    #                         allIPs.append(thisAddr)
    #
    #     print ("allIPs", allIPs)
    #     return allIPs[0] # I think it should only be address one anyway

    def getBoardType(self):
        """ Returns the version of the board """
        return self.board_type

    def setImpedance(self, flag):
        """ Enable/disable impedance measure """
        self.impedance = bool(flag)

    def connect(self):
        """ Connect to the board and configure it. Note: recreates various objects upon call. """
        if self.ip_address is None:
            raise ValueError('self.ip_address cannot be None')

        if self.log:
            print("Init WiFi connection with IP: " + self.ip_address)

        """
        Docs on these HTTP requests and more are found:
        https://app.swaggerhub.com/apis/pushtheworld/openbci-wifi-server/1.3.0
        """

        res_board = requests.get("http://%s/board" % self.ip_address)

        if res_board.status_code == 200:
            board_info = res_board.json()
            if not board_info['board_connected']:
                raise RuntimeError("No board connected to WiFi Shield. Learn at docs.openbci.com")
            self.board_type = board_info['board_type']
            self.eeg_channels_per_sample = board_info['num_channels']
            if self.log:
                print("Connected to %s with %s channels" % (self.board_type, self.eeg_channels_per_sample))

        gains = None
        if self.board_type == k.BOARD_CYTON:
            gains = [24, 24, 24, 24, 24, 24, 24, 24]
            self.daisy = False
        elif self.board_type == k.BOARD_DAISY:
            gains = [24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24]
            self.daisy = True
        elif self.board_type == k.BOARD_GANGLION:
            gains = [51, 51, 51, 51]
            self.daisy = False
        self.local_wifi_server.set_daisy(daisy=self.daisy)
        self.local_wifi_server.set_parser(ParseRaw(gains=gains, board_type=self.board_type))

        if self.high_speed:
            output_style = 'raw'
        else:
            output_style = 'json'
        if self.useTCP:
            request_url = "http://%s/tcp"
        else:
            request_url = "http://%s/udp"

        if not self.useTCP:
            self.local_wifi_server.start_udp_handler()

        res_tcp_post = requests.post(request_url % self.ip_address,
                          json={
                                'ip': self.local_ip_address,
                                'port': self.local_wifi_server_port,
                                'output': output_style,
                                'delimiter': True,
                                'latency': self.latency
                                })
        # print(res_tcp_post)
        if res_tcp_post.status_code == 200:
            try:
                tcp_status = res_tcp_post.json()
                if tcp_status['connected']:
                    if self.log:
                        if self.useTCP:
                            print("WiFi Shield to Python TCP Socket Established")
                        else:
                            print("WiFi Shield to Python through UDP Established")
                else:
                    raise RuntimeWarning("WiFi Shield is not able to connect to local server. Please open an issue.")
            except Exception as e:
                print("error in processing response request: ", e)
                print("response: ", res_tcp_post)
                pass


    def init_streaming(self):
        """ Tell the board to record like crazy. """
        res_stream_start = requests.get("http://%s/stream/start" % self.ip_address)
        if res_stream_start.status_code == 200:
            self.streaming = True
            self.packets_dropped = 0
            self.time_last_packet = timeit.default_timer()
        else:
            raise EnvironmentError("Unable to start streaming. Check API for status code %d on /stream/start" % res_stream_start.status_code)

    def find_wifi_shield(self, shield_name=None, wifi_shield_cb=None):
        """Detects Ganglion board MAC address -- if more than 1 around, will select first. Needs root privilege."""

        if self.log:
            print("Scanning nearby devices for %d seconds..." % self.timeout)

        list_ip = []
        list_id = []
        found_shield = False

        def wifi_shield_found(response):
            res = requests.get(response.location, verify=False).text
            # print("res:", res)
            device_description = xmltodict.parse(res)
            try:
                cur_shield_name = str(device_description['root']['device']['serialNumber'])
                cur_base_url = str(device_description['root']['URLBase'])
                cur_ip_address = re.findall(r'[0-9]+(?:\.[0-9]+){3}', cur_base_url)[0]
                list_id.append(cur_shield_name)
                list_ip.append(cur_ip_address)
                found_shield = True
                print("Found WiFi Shield %s with IP Address %s" % (cur_shield_name, cur_ip_address))
                if shield_name is None:
                    # print("Found WiFi Shield %s with IP Address %s" % (cur_shield_name, cur_ip_address))
                    if wifi_shield_cb is not None:
                        # print("Proceeding with WiFi Shield %s" % (cur_shield_name))
                        wifi_shield_cb(cur_ip_address, cur_shield_name, device_description)
                else:
                    if shield_name == cur_shield_name:
                        if wifi_shield_cb is not None:
                            # print("Proceeding with WiFi Shield %s" % (cur_shield_name))
                            wifi_shield_cb(cur_ip_address, cur_shield_name, device_description)
            except Exception as e:
                print("exception in discovery")
                pass

        ssdp_hits = ssdp.discover("urn:schemas-upnp-org:device:Basic:1", timeout=self.timeout, wifi_found_cb=wifi_shield_found, all_ip_addresses=self.local_ip_addresses) # send multicast on all local interfaces
        # ssdp_hits = ssdp.discover("urn:schemas-upnp-org:device:Basic:1", timeout=self.timeout, wifi_found_cb=wifi_shield_found)

        nb_wifi_shields = len(list_id)

        if nb_wifi_shields < 1:
            # print("No WiFi Shields found ;(")
            raise OSError('Cannot find OpenBCI WiFi Shield with local name')

        # we're not using this anyway
        # if nb_wifi_shields > 1:
        #     print(
        #         "Found " + str(nb_wifi_shields) +
        #         ", selecting first named: " + list_id[0] +
        #         " with IPV4: " + list_ip[0])
        #     return list_ip[0]

    def wifi_write(self, output):
        """
        Pass through commands from the WiFi Shield to the Carrier board
        :param output:
        :return:
        """
        res_command_post = requests.post("http://%s/command" % self.ip_address,
                                         json={'command': output})
        if res_command_post.status_code == 200:
            ret_val = res_command_post.text
            if self.log:
                print(ret_val)
            return ret_val
        else:
            if self.log:
                print("Error code: %d %s" % (res_command_post.status_code, res_command_post.text))
            raise RuntimeError("Error code: %d %s" % (res_command_post.status_code, res_command_post.text))

    def getSampleRate(self):
        return self.sample_rate

    def getNbEEGChannels(self):
        """Will not get new data on impedance check."""
        return self.eeg_channels_per_sample

    def start_streaming(self, callback, lapse=-1):
        """
        Start handling streaming data from the board. Call a provided callback
        for every single sample that is processed
        Args:
          callback: A callback function -- or a list of functions -- that will receive a single argument of the
              OpenBCISample object captured.
        """
        start_time = timeit.default_timer()

        if self.local_wifi_server is not None:
            # Enclose callback funtion in a list if it comes alone
            if not isinstance(callback, list):
                self.local_wifi_server.set_callback(callback)
            else:
                self.local_wifi_server.set_callback(callback[0])

            if not self.streaming:
                self.init_streaming()

        # while self.streaming:
        #     # should the board get disconnected and we could not wait for notification anymore, a reco should be attempted through timeout mechanism
        #     try:
        #         # at most we will get one sample per packet
        #         self.waitForNotifications(1. / self.getSampleRate())
        #     except Exception as e:
        #         print("Something went wrong while waiting for a new sample: " + str(e))
        #     # retrieve current samples on the stack
        #     samples = self.delegate.getSamples()
        #     self.packets_dropped = self.delegate.getMaxPacketsDropped()
        #     if samples:
        #         self.time_last_packet = timeit.default_timer()
        #         for call in callback:
        #             for sample in samples:
        #                 call(sample)
        #
        #     if (lapse > 0 and timeit.default_timer() - start_time > lapse):
        #         self.stop();
        #     if self.log:
        #         self.log_packet_count = self.log_packet_count + 1;
        #
        #     # Checking connection -- timeout and packets dropped
        #     self.check_connection()

    def test_signal(self, signal):
        #FIXME: 0 (']' char) doesn't disable the test! it changes square wave's freqency
        """ Enable / disable test signal """
        if signal == 0:
            self.warn("Disabling synthetic square wave")
            try:
                self.wifi_write(']')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        elif signal == 1:
            self.warn("Eisabling synthetic square wave")
            try:
                self.wifi_write('[')
            except Exception as e:
                print("Something went wrong while setting signal: " + str(e))
        else:
            self.warn("%s is not a known test signal. Valid signal is 0-1" % signal)

    def set_channel(self, channel, toggle_position): #FIXME: doesn't address all channels on cyton/daisy
        """ Enable / disable channels """
        try:
            # Commands to set toggle to on position
            if toggle_position == 1:
                if channel is 1:
                    self.wifi_write('!')
                if channel is 2:
                    self.wifi_write('@')
                if channel is 3:
                    self.wifi_write('#')
                if channel is 4:
                    self.wifi_write('$')
            # Commands to set toggle to off position
            elif toggle_position == 0:
                if channel is 1:
                    self.wifi_write('1')
                if channel is 2:
                    self.wifi_write('2')
                if channel is 3:
                    self.wifi_write('3')
                if channel is 4:
                    self.wifi_write('4')
        except Exception as e:
            print("Something went wrong while setting channels: " + str(e))

    def set_sample_rate(self, sample_rate):
        """ Change sample rate """
        try:
            if self.board_type == k.BOARD_CYTON:
                if sample_rate == 250:
                        self.wifi_write('~6')
                elif sample_rate == 500:
                        self.wifi_write('~5')
                elif sample_rate == 1000:
                        self.wifi_write('~4')
                elif sample_rate == 2000:
                        self.wifi_write('~3')
                elif sample_rate == 4000:
                        self.wifi_write('~2')
                elif sample_rate == 8000:
                        self.wifi_write('~1')
                elif sample_rate == 16000:
                        self.wifi_write('~0')
                else:
                    print("Sample rate not supported: " + str(sample_rate))
            elif self.board_type == k.BOARD_GANGLION:
                if sample_rate == 200:
                        self.wifi_write('~7')
                elif sample_rate == 400:
                        self.wifi_write('~6')
                elif sample_rate == 800:
                        self.wifi_write('~5')
                elif sample_rate == 1600:
                        self.wifi_write('~4')
                elif sample_rate == 3200:
                        self.wifi_write('~3')
                elif sample_rate == 6400:
                        self.wifi_write('~2')
                elif sample_rate == 12800:
                        self.wifi_write('~1')
                elif sample_rate == 25600:
                        self.wifi_write('~0')
                else:
                    print("Sample rate not supported: " + str(sample_rate))
            else:
                print("Board type not supported for setting sample rate")
        except Exception as e:
            print("Something went wrong while setting sample rate: " + str(e))

    def set_accelerometer(self, toggle_position):
        """ Enable / disable accelerometer """
        try:
            if self.board_type == k.BOARD_GANGLION:
                # Commands to set toggle to on position
                if toggle_position == 1:
                    self.wifi_write('n')
                # Commands to set toggle to off position
                elif toggle_position == 0:
                    self.wifi_write('N')
            else:
                print("Board type not supported for setting accelerometer")
        except Exception as e:
            print("Something went wrong while setting accelerometer: " + str(e))

    """
    Clean Up (atexit)
    """

    def stop(self):
        print("Stopping streaming...")
        self.streaming = False
        # connection might be already down here
        try:
            if self.impedance:
                print("Stopping with impedance testing")
                self.wifi_write('Z')
            else:
                self.wifi_write('s')
        except Exception as e:
            print("Something went wrong while asking the board to stop streaming: " + str(e))
        if self.log:
            logging.warning('sent <s>: stopped streaming')

    def disconnect(self):
        if self.streaming:
            self.stop()

        # should not try to read/write anything after that, will crash

    """
        SETTINGS AND HELPERS
    """

    def warn(self, text):
        if self.log:
            # log how many packets where sent succesfully in between warnings
            if self.log_packet_count:
                logging.info('Data packets received:' + str(self.log_packet_count))
                self.log_packet_count = 0
            logging.warning(text)
        print("Warning: %s" % text)

    def check_connection(self):
        """ Check connection quality in term of lag and number of packets drop. Reinit connection if necessary. FIXME: parameters given to the board will be lost."""
        # stop checking when we're no longer streaming
        if not self.streaming:
            return
        # check number of dropped packets and duration without new packets, deco/reco if too large
        if self.packets_dropped > self.max_packets_to_skip:
            self.warn("Too many packets dropped, attempt to reconnect")
            self.reconnect()
        elif self.timeout > 0 and timeit.default_timer() - self.time_last_packet > self.timeout:
            self.warn("Too long since got new data, attempt to reconnect")
            # if error, attempt to reconect
            self.reconnect()

    def reconnect(self):
        """ In case of poor connection, will shut down and relaunch everything. FIXME: parameters given to the board will be lost."""
        self.warn('Reconnecting')
        self.stop()
        self.disconnect()
        self.connect()
        self.init_streaming()


class WiFiShieldHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, callback=None, high_speed=True,
                 parser=None, daisy=False, useTCP=True):
        asyncore.dispatcher_with_send.__init__(self, sock)

        self.callback = callback
        self.daisy = daisy
        self.high_speed = high_speed
        self.last_odd_sample = OpenBCISample()
        self.parser = parser if parser is not None else ParseRaw(gains=[24, 24, 24, 24, 24, 24, 24, 24])
        self.useTCP = useTCP

    def handle_write(self):
        if self.useTCP:
            self.initiate_send()
        else:
            pass

    def writable(self):
        if not self.useTCP:
            return False # don't want write notifies - otherwise cpu usage goes high

    def handle_read(self):
        if self.useTCP:
            data = self.recv(3000)  # 3000 is the max data the WiFi shield is allowed to send over TCP
        else:
            # data = self.recvfrom(3000) #not available in asyncore
            data = self.recv(3000) # doesn't provide address where the data comes from
        # print(data)
        if len(data) > 2:
            if self.high_speed:
                packets = int(len(data)/33)
                raw_data_packets = []
                for i in range(packets):
                    raw_data_packets.append(bytearray(data[i * k.RAW_PACKET_SIZE: i * k.RAW_PACKET_SIZE + k.RAW_PACKET_SIZE]))
                    # print(bytearray(data[i * k.RAW_PACKET_SIZE: i * k.RAW_PACKET_SIZE + k.RAW_PACKET_SIZE]))
                samples = self.parser.transform_raw_data_packets_to_sample(raw_data_packets=raw_data_packets)

                for sample in samples:
                    # if a daisy module is attached, wait to concatenate two samples (main board + daisy)
                    #  before passing it to callback
                    if self.daisy:
                        # odd sample: daisy sample, save for later
                        if ~sample.sample_number % 2:
                            self.last_odd_sample = sample
                        # even sample: concatenate and send if last sample was the fist part, otherwise drop the packet
                        elif sample.sample_number - 1 == self.last_odd_sample.sample_number:
                            # the aux data will be the average between the two samples, as the channel
                            # samples themselves have been averaged by the board
                            daisy_sample = self.parser.make_daisy_sample_object_wifi(self.last_odd_sample, sample)
                            if self.callback is not None:
                                self.callback(daisy_sample)
                    else:
                        if self.callback is not None:
                            self.callback(sample)

            else:
                try:
                    possible_chunks = data.split('\r\n')
                    if len(possible_chunks) > 1:
                        possible_chunks = possible_chunks[:-1]
                    for possible_chunk in possible_chunks:
                        if len(possible_chunk) > 2:
                            chunk_dict = json.loads(possible_chunk)
                            if 'chunk' in chunk_dict:
                                for sample in chunk_dict['chunk']:
                                    if self.callback is not None:
                                        self.callback(sample)
                            else:
                                print("not a sample packet")
                except ValueError as e:
                    print("failed to parse: %s" % data)
                    print(e)
                except BaseException as e:
                    print(e)


class WiFiShieldServer(asyncore.dispatcher):

    def __init__(self, host, port, callback=None, gains=None, high_speed=True, daisy=False, useTCP=True):
        asyncore.dispatcher.__init__(self)
        self.useTCP = useTCP
        print("useTCP:", self.useTCP)
        if self.useTCP:
            socket_type = socket.SOCK_STREAM
        else:
            socket_type = socket.SOCK_DGRAM
        self.create_socket(socket.AF_INET, socket_type)
        self.bind((host, port))
        self.set_reuse_addr()
        self.daisy = daisy
        if self.useTCP:
            self.listen(5)
        self.callback = None
        self.handler = None
        self.parser = ParseRaw(gains=gains)
        self.high_speed = high_speed
        # print("socket: ", self.socket)
        print("WiFiShieldServer ready")

    def start_udp_handler(self):
        if not self.useTCP:
            self.handler = WiFiShieldHandler(self.socket, self.callback, high_speed=self.high_speed, parser=self.parser, daisy=self.daisy, useTCP=self.useTCP)
            print("UDP handler started")
        else:
            print("udp handler only allower it using UDP ")

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print('Incoming connection from %s' % repr(addr))
            self.handler = WiFiShieldHandler(sock, self.callback, high_speed=self.high_speed,
                                             parser=self.parser, daisy=self.daisy, useTCP=self.useTCP)

    def set_callback(self, callback):
        self.callback = callback
        if self.handler is not None:
            self.handler.callback = callback

    def set_daisy(self, daisy):
        self.daisy = daisy
        if self.handler is not None:
            self.handler.daisy = daisy

    def set_gains(self, gains):
        self.parser.set_ads1299_scale_factors(gains)

    def set_parser(self, parser):
        self.parser = parser

    # def writable(self):
        # if not self.useTCP:
            # return False # don't want write notifies
