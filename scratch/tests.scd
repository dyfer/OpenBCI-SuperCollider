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



// ~recv = OSCdef(\portRec, {|msg| msg.postln;~port = msg[1]}, '/OpenBCI-536D/receivePort');
~recv = OSCdef(\portRec, {|msg| msg.postln;~port = msg[1]}, '/obci/receivePort');
~disc = OSCdef(\disc, {|msg| msg.postln}, '/obci/found');
"/usr/local/bin/python3".unixCmdGetStdOut
~port = 56494
File.exists("/Volumes/data/Dokumenty/src/SC/OpenBCI-SuperCollider/python/openbci_wifi_osc.py")
//add reporting on connected/disconnected
File.exists("/Volumes/data/Dokumenty/src/brain/OpenBCI-SuperCollider/python/openbci_wifi_osc.py")
"/Volumes/data/Dokumenty/src/SC/OpenBCI-SuperCollider/python/"
~pid =
"export PATH=/usr/local/bin; python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py".unixCmdGetStdOut

~pid = "/usr/local/bin/python3 -u /Volumes/data/Dokumenty/src/SC/OpenBCI-SuperCollider/python/openbci_wifi_osc.py".unixCmd

~pid = "python3 /Volumes/data/Dokumenty/src/SC/OpenBCI-SuperCollider/python/openbci_wifi_osc.py".runInTerminal

~pid = "python3 /Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py --address /obci".runInTerminal

~pid
pidRunning
("kill" + ~pid).unixCmd;

thisProcess.platform.killAll("Python")
thisProcess.platform.killProcessByID(~pid);

"export PATH=/usr/local/bin; python3".unixCmd

NetAddr.langPort
OpenBCI.allIPs

(
//get port etc
~recv = OSCdef(\portRec, {|msg| msg.postln;~port = msg[1]}, '/obci/receivePort');
~disc = OSCdef(\disc, {|msg| msg.postln}, '/obci/found');
)

OSCFunc.trace(true)
OSCFunc.trace(false)
NetAddr.langPort

OpenBCI.
a = IdentityDictionary()
a[\ss] = 12323
a.free
a.removeAll
a

IdentityDictionary

NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.115")
NetAddr("localhost", ~port).sendMsg('/connect', "192.168.200.116") //home
NetAddr("localhost", ~port).sendMsg('/connect', "192.168.1.4") //home
NetAddr("localhost", ~port).sendMsg('/start_streaming')
NetAddr("localhost", ~port).sendMsg('/stop_streaming');
NetAddr("localhost", ~port).sendMsg('/quit')

NetAddr("localhost", 51530).sendMsg('/stop_streaming');

NetAddr("localhost", ~port).sendMsg('/receivePort')
NetAddr("localhost", ~port).sendMsg('/quit')
NetAddr("localhost", ~port).sendMsg('/discover') //timeout, numAttempts
NetAddr("localhost", ~port).sendMsg('/discover', 10, 10) //timeout, numAttempts
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.113")
NetAddr("localhost", ~port).sendMsg('/connect', "OpenBCI-5381")
NetAddr("localhost", ~port).sendMsg('/connect', "OpenBCI-536D")
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.138")
NetAddr("localhost", ~port).sendMsg('/connect', "10.45.0.143")
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

~vars[\events].eventDict['/obci/2_scope'].data[\plotter].scope.scope.lineWidth_(20000000)
~vars[\events].eventDict['/obci/2_plot'].data[\plotter].scopeView.lineWidth_(30)
~vars[\events].eventDict['/obci/2_scope'].data[\plotter].scope.synth.set(\inMul, 0)
~vars[\events].eventDict['/obci/2_scope'].data[\plotter].scope.synth.set(\inMul, 0.001)
~vars[\events].eventDict['/obci/2_scope'].data[\plotter].scope.synth.set(\impulseDiv, 2)
"python3".runInTerminal

// ~formatStr = {|val, numChars|
// if(val.isKindOf(SimpleNumber), {
LivePlotter

~genRec.free; ~genRec = OSCdef(\genRec, {|msg| "gen: ".post; msg.round(0.001).asString.padLeft(6).postln;}, '/obci');

OSCdef(\genRec2, {|msg| "gen2: ".post; msg.round(0.001).asString.padLeft(6).postln;}, '/obci2');


0.1.asString.padLeft(6).padRight(7, "0")
0.1.asStringPrec(3)

OpenBCI.startDiscovery
OpenBCI.stopDiscovery

OpenBCI.allIPs.keys
OpenBCI.runInTerminal = false
OpenBCI.runInTerminal = true

b = Cyton.wifi('OpenBCI-5381', {|da|"1: ".post; da.round(0.001).postln}).connect
c = Cyton.wifi('OpenBCI-8435', {|da|"2: ".post; da.round(0.001).postln})
b.dataAction={}
b.dataAction={|da|da.postln}
b.pythonPort
b.isConnected //status
b.connect
b.stop
b.start
b.start(Bus.new(\control, 0, 12, s))

FreqScope2

~buf = Buffer.alloc(s, 1, 12);
b.start(~buf)
s.dumpOSC
s.dumpOSC(0)
c.connect
c.start

~buf.plot0
~buf.bufnum
~buf.getToFloatArray(action: {|arr| arr.postln})

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
s.boot
s.addr.port
b.sendMsg('/start_streaming', s.addr.ip, s.addr.port, '/c_setn', 0)
b.sendMsg('/start_streaming', s.addr.ip, s.addr.port, '/c_setn', 0)
s.scope(12, 0, rate: \control)

Bus.new(\control, 0, 12, s).getnSynchronous

Bus.new(\control, 0, 20, s).index
Buffer.new(s, 1, 12, 2).bufnum


f = FreqScope2(Bus.new(\control, 3, 8, s), 512, ampdb: false)

f.scope.synth.set(\inMul, 1000)


~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].setDefaultChannelSettings
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].dump
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].stop
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].start(b)
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].start(c)
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].start
~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].test2AmpSlow

~vars[\events].eventDict['OpenBCI-5381'].data[\buffer].plot0
Cyton

~vars[\events].eventDict['OpenBCI-5381'].data[\obciWiFi].dataAction = {|da| da.postln}

~vars[\events].eventDict['/obci/0'].data[\rawBusKr].scope
~vars[\events].eventDict['/obci/0'].data[\processedBusKr].scope

b = Buffer.alloc(s, 1, 12);
p = b.plot0
c = Bus.control(s, 12)
c.scope

s.dumpOSC
s.dumpOSC(0)
b.bufnum
b.plot
b.getToFloatArray(action: {|arr| arr.postln})

Server.supernova
s.boot

OpenBCI.runInTerminal = true

b.bufnum
s.
firstInputChannel

~buf.bufnum
~buf.setn(0, [85, -0.1875, -0.1875, -0.1875, -0.1875, -0.1875, -0.1875, -0.1875, -0.1875, 0,0,0])
[int32:1, int32:0, int32:12, float32:85, float32:-0.1875, float32:-0.1875, float32:-0.1875, float32:-0.1875, float32:-0.1875, float32:-0.1875, float32:-0.1875, float32:-0.1875]

s.addr.sendMsg("/b_setn", 0, 0, 9, 204, -0.166113, -0.1875, -0.105182, -0.139488, -0.134019, -0.146482, -0.18037, -0.178661)

b.setn(0, [204.0, -0.166113, -0.1875, -0.105182, -0.139488, -0.134019, -0.146482, -0.18037, -0.178661])

Buffer

b.responders[0].enabled
b = Cyton.wifi('OpenBCI-5381', {|da|"1: ".post; da.round(0.001).postln}).connect
c = Cyton.wifi('OpenBCI-8435', {|da|"2: ".post; da.round(0.001).postln}).connect
b.dataAction={}
b.dataAction={|da|da.postln}
b.pythonPort
b.isConnected //status
b.connect
b.isStreaming
b.stop
b.start
b.start(Bus.new(\control, 0, 12, s))
Server.supernova
s.options.numInputBusChannels = 8
b.testDC
p = SFPlayer().gui
p = SFPlayer("/Volumes/JACK2017-18/2018.02\ JACK/run\ through/mixdown/180209_154435.wav").gui; //JACK stereo mixdown
p.free
s.scope


~buf = Buffer.alloc(s, 1, 12);
b.start(~buf)
s.dumpOSC
s.dumpOSC(0)
c.connect
c.start
c.stop
s.plotTree
c.free

	~buf.plot
b.free

~buf.plot0
~buf.bufnum
~buf.getToFloatArray(action: {|arr| arr[1..4].round(0.000001).postln})
~buf.getToFloatArray(action: {|arr| arr.postln})
(
~scaleVal = {arg val, vref = 4.5, gain = 24;
	var ads1299_Vref = vref;  //reference voltage for ADC in ADS1299.  set by its hardware
	var ads1299_gain = gain;  //assumed gain setting for ADS1299.  set by its Arduino code
	var scale_fac = ads1299_Vref / (pow(2, 23)-1) / ads1299_gain  * 1000000; //From: OpenBCI_GUI - ADS1299 datasheet Table 7, confirmed through experiment
	val * scale_fac
}
)

~scaleVal.(-3763.27, gain: 24) //from openbci.... ???
//from ADS1299 specs
// /Test signal amplitude
// These bits determine the calibration signal amplitude.
// 0 : 1 × –(VREFP – VREFN) / 2400
// 1 : 2 × –(VREFP – VREFN) / 2400
-3763.27 / -1000000

4.5/2400 * 2 //WE GET THIS VALUE FROM THE WIFI SHIELD!

OSCFunc.trace
OSCFunc.trace(false)

Server.supernova

l = List()
l.add("123")
l.addAll([1, 2, "sdsds"])


//----
//udp
"\xa0\x02\xfa\xc5n\xfa\xba\xd4\xfa\xael\xfa\xb4,\x9d\xd0\xd2\x94n\x90\x9b\x8d}\x98 \xb9\x00\x00\x00\x00\x00\x00\xc0\xa0\x03\xfa\xc5\xa3\xfa\xbb\x08\xfa\xae\xa3\xfa\xb4_\x9d\xd1\x14\x94n\xcf\x9b\x8d\xbe\x98 \xf6\x00\x00\x00\x00\x00\x00\xc0\xa0\x04\xfa\xc5s\xfa\xba\xd3\xfa\xaeo\xfa\xb4'\x9d\xd0\xe0\x94n\x99\x9b\x8d\x8d\x98 \xc0\x00\x00\x00\x00\x00\x00\xc0"
//tcp
'\xa0\x01\xfa\xcd\xc5\xfa\xc2\xc2\xfa\xba\x0e\xfa\xc1\x8f\xa0\x9c\x87\x976\xcf\x9e\x1dW\x9b\xbd\xbe\x00\x00\x00\x00\x00\x00\xc0\xa0\x02\xfa\xcd\n\xfa\xc2\x0b\xfa\xb9X\xfa\xc0\xdc\xa0\x9b\xd9\x976\x1e\x9e\x1c\xa9\x9b\xbd\x0e\x00\x00\x00\x00\x00\x00\xc0'

~vars[\events].eventDict[\vbapSetup].data.add(\speakerArray -> [1,2,3])
~vars[\events].eventDict[\vbap].data[\vbapSpeakerArray].numSpeakers
~vars[\events].eventDict[\vbapSetup].data[\speakerArray]
~vars[\events].eventDict[\vbap].isRunning
