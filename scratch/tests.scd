OSCFunc.trace
OSCFunc.trace(false)
s.quit
NetAddr.langPort


n = NetAddr("10.45.0.113", 80)
n.connect

setenv

"which python3".unixCmdGetStdOut.size
"PATH".setenv("PATH".getenv++":/usr/local/bin")
"PATH".getenv
"which python3".unixCmdGetStdOut.size
a =

File.exists("which python3".unixCmdGetStdOut.standardizePath)
"which python".unixCmdGetStdOut
.size
p = (a.standardizePath + "--help").unixCmd
p
"python --help".unixCmdGetStdOut

p = "python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py".unixCmd
("kill"+p).unixCmd

n.sendMsg("test")

NetAddr("localhost", 61121).sendMsg('/receivePort')
NetAddr("localhost", 64676).sendMsg('/quit')



~recv = OSCdef(\portRec, {|msg| ~port = msg[1]}, '/obci/receivePort');
~disc = OSCdef(\disc, {|msg| msg.postln}, '/obci/found');

~port = 56494

//add reporting on connected/disconnected

~pid =
"export PATH=/usr/local/bin; python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py".unixCmdGetStdOut

~pid = "/usr/local/bin/python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py".unixCmd

~pid = "python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py".runInTerminal

~pid = "python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py --address /obci2".runInTerminal

~pid
pidRunning
("kill" + ~pid).unixCmd;

"export PATH=/usr/local/bin; python3".unixCmd

NetAddr("localhost", 51530).sendMsg('/connect', "10.45.0.113")
NetAddr("localhost", 51530).sendMsg('/start_streaming')
NetAddr("localhost", ~port).sendMsg('/stop_streaming'); NetAddr("localhost", 51530).sendMsg('/stop_streaming');

NetAddr("localhost", ~port).sendMsg('/receivePort')
NetAddr("localhost", ~port).sendMsg('/quit')
NetAddr("localhost", ~port).sendMsg('/discover') //timeout, numAttempts
NetAddr("localhost", ~port).sendMsg('/discover', 10, 10) //timeout, numAttempts
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.113")
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.138")
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.113", 250, 20, 1000, 3, 5)
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.113", 250, 20, 1000, 3, 5)
//def connect(unused_addr, addressOrName, sample_rate=None, max_packets_to_skip=20, latency=10000, timeout=3, attempts=5):
NetAddr("localhost", ~port).sendMsg('/start_streaming')
NetAddr("localhost", ~port).sendMsg('/stop_streaming')

// NetAddr("localhost", ~port).sendMsg('/test_signal', 1)
// NetAddr("localhost", ~port).sendMsg('/test_signal', 0)
NetAddr("localhost", ~port).sendMsg('/send_command', "[") //test square wave
NetAddr("localhost", ~port).sendMsg('/send_command', "!") //activate 1st channel
NetAddr("localhost", ~port).sendMsg('/send_command', "1") //deactivate 1st channel
// NetAddr("localhost", ~port).sendMsg('/send_command', "b") //start after stopping
NetAddr("localhost", ~port).sendMsg('/send_command', "d") //default settings
// NetAddr("localhost", ~port).sendMsg('/send_command', "s") //stop streaming
NetAddr("localhost", ~port).sendMsg('/send_command', "~6") //sampling rate: 250Hz
NetAddr("localhost", ~port).sendMsg('/send_command', "~4") //sampling rate: 1000Hz
~4

NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.113"); NetAddr("localhost", ~port).sendMsg('/start_streaming')

"python3".runInTerminal

// ~formatStr = {|val, numChars|
// if(val.isKindOf(SimpleNumber), {

~genRec.free; ~genRec = OSCdef(\genRec, {|msg| "gen: ".post; msg.round(0.001).asString.padLeft(6).postln;}, '/obci');

OSCdef(\genRec2, {|msg| "gen2: ".post; msg.round(0.001).asString.padLeft(6).postln;}, '/obci2');


0.1.asString.padLeft(6).padRight(7, "0")
0.1.asStringPrec(3)

OpenBCI.startDiscovery
OpenBCI.stopDiscovery

OpenBCI.allIPs.keys

b = Cyton.wifi('OpenBCI-5381', {|da|"1: ".post; da.round(0.001).postln})
c = Cyton.wifi('OpenBCI-8435', {|da|"2: ".post; da.round(0.001).postln})
b.dataAction={}
b.dataAction={|da|da.postln}
b.pythonPort
b.connect
b.start

c.connect
c.start

b.stop
b.free
b.setDefaultChannelSettings
b.getDefaultChannelSettings
b.test1AmpSlow
b.sendMsg('/send_command', "[")
b.sendMsg('/send_command', "$]")
b.put($d.asString)
b.put("d")
b.setSampleRate(4)
b.setSampleRateHz(249)


