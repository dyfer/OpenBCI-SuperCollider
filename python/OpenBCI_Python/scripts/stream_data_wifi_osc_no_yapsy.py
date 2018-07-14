import sys; sys.path.append('..') # help python find cyton.py relative to scripts folder
sys.path.append('.')
from openbci import wifi as bci
import logging
import streamer_osc_sc
# from openbci.plugins.streamer_osc import StreamerOSC
# from yapsy.PluginManager import PluginManager

# trying to use plugin PluginManager
# manager = PluginManager()


def printData(sample):
    print(sample.sample_number)
    print(sample.channel_data)

def sendData(sample):
    # print(sample)
    # osc.plugin_object(sample)
    osc(sample)
    print(sample.sample_number)
    # print(sample.channel_data)


if __name__ == '__main__':
    # shield_name = 'OpenBCI-W222'
    shield_name = 'OpenBCI-5381'
    # shield_name = None
    logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
    logging.info('---------LOG START-------------')

    # yapsy
    # plugins_paths = ["openbci/plugins"]
    # if args.plugins_path:
        # plugins_paths += args.plugins_path
    # manager.setPluginPlaces(plugins_paths)
    # manager.collectPlugins()

    # print ("Found plugins:")
    # for plugin in manager.getAllPlugins():
        # print ("[ " + plugin.name + " ]")
    # print("\n")

    # osc = manager.getPluginByName("streamer_osc")
    osc = streamer_osc_sc.StreamerOSC(ip='localhost', port=57120, address="/obci0")
    osc.activate()


    # osc.plugin_object.pre_activate(['localhost', 57120, "/obci0"], sample_rate=250, eeg_channels=8, aux_channels=3, imp_channels=0)
    # osc.plugin_object.pre_activate(['localhost', 57120, "/obci0"], sample_rate=250, eeg_channels=8, aux_channels=3, imp_channels=0)

    # osc.plugin_object.ip='localhost'
    # osc.plugin_object.port=57120
    # osc.plugin_object.address="/obci0"

    # print("osc.plugin_object.port", osc.plugin_object.port)


    def list_found_shields(ip_address, name, description):
        print("In stream_data... Found WiFi Shield %s with IP Address %s" % (name, ip_address))


    # osc = StreamerOSC(ip='localhost', port = 57120, address="/obci0")
    # osc.activate();

    # shield = bci.OpenBCIWiFi(shield_name=None, log=True, high_speed=False, shield_found_cb=list_found_shields)
    shield = bci.OpenBCIWiFi(shield_name=shield_name, log=True, high_speed=False)
    # shield = bci.OpenBCIWiFi(ip_address='10.45.0.113', log=True, high_speed=False)
    # print("shield.local_wifi_server:", shield.local_wifi_server)
    if shield.local_wifi_server is not None:
        print("WiFi Shield Instantiated")
        # shield.start_streaming(printData)
        shield.start_streaming(sendData)

        shield.loop()
