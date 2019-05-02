//--abstract class for supercollider openbci communication

//related: Cyton Ganglion

//wifi requires python3 and forked OpenBCI_Python (included)

OpenBCI {
	var <port, task;
	var <>dataAction, <>replyAction, <>initAction;  //callback functions
	var <latency; //for wifi: if latency > 0, Python will send messages with timestamp offset by latency to ensure timely processing by the server; this is necessary to avoid senting multiple messages within control period!
	var <>accelAction;  //more callback functions
	var <>data, <>accel;  //latest readings (can be nil)
	var <name, <ip, <responders, <pid, <cmd, <pythonNetAddr;
	var <wifi=false, <pythonPort, <thisOscPrefix, <thisOscPath;
	var msgList;
	var <isConnected = false, <isStreaming = false;
	var <>postMessages = true;
	var freeFunc;

	classvar <allIPs, <pythonPath = "python3", <pythonFound = false;
	classvar <>globalOscPrefix = "";
	classvar <>runInTerminal = false; //for testing, macOS only
	// classvar <scriptPath = "/Volumes/data/Dokumenty/src/brain/OpenBCI_Python/scripts/openbci_wifi_osc.py";
	classvar <scriptPath;
	classvar <discoveryPid, <>discoveryAddr = '/obci/discovery', <discoveryResp;

	*initClass {
		allIPs = IdentityDictionary();
		scriptPath = thisProcess.platform.formatPathForCmdLine(File.realpath(this.class.filenameSymbol).dirname.withTrailingSlash ++ "python/openbci_wifi_osc.py");
	}

	*new {|port, baudrate= 115200, dataAction, replyAction, initAction|
		^super.new.initOpenBCI(port, baudrate, dataAction, replyAction, initAction);
	}

	//name (unique) is required, IP is optional (can be inferred using service discovery)
	//wifi shield name will be taken from name, unless specified later

	*wifi {|name, dataAction, replyAction, initAction, latency = 0.05|
		^super.new.initOpenBCIwifi(name, dataAction, replyAction, initAction, latency);
	}

	//helpers
	*startDiscovery {|onDoneAction = ({})|
		var cmd;
		// allIPs ?? {allIPs = IdentityDictionary()};
		discoveryResp = OSCFunc({|msg|
			var thisName, thisIP;
			thisName = msg[2];
			thisIP = msg[1];
			if(allIPs[thisName].isNil, {
				allIPs[thisName.asSymbol] = thisIP;
				format("Found new WiFi shield % at %", thisName, thisIP).postln;
				format("Total number of WiFi shields found: %", allIPs.size).postln;
			})
		}, discoveryAddr ++ '/found');
		"PATH".setenv("PATH".getenv++":/usr/local/bin");//for homebrew on macos
		// cmd = pythonPath + scriptPath + "--host localhost" + "--port" + NetAddr.langPort + "--address" + discoveryAddr + "--discover";
		// cmd = pythonPath + "-u" + scriptPath + "--host localhost" + "--port" + NetAddr.langPort + "--address" + discoveryAddr + "--discover";
		cmd = format("% -u  % --host localhost --port % --address % --discover", pythonPath, scriptPath, NetAddr.langPort, discoveryAddr);
		"cmd: ".post; cmd.postln;
		discoveryPid = cmd.unixCmd({
			discoveryResp.free;
			discoveryPid = nil;
			"Discovery finised. ".postln;
			"allIPs: ".post; allIPs.postln;
			format("Total number of WiFi shields found: %", allIPs.size).postln;
			onDoneAction.();
		}); //no auto free - in case we want to restart it? but maybe responders should be tied to it?
		"Discovery started... ".postln;
	}

	*stopDiscovery { //call this with a timer from discoverWiFi?
		discoveryPid !? {("kill" + discoveryPid).unixCmd};
	}

	*saveAllIPs {|path|
		if(allIPs.notNil, {
			format("Saving name/IP dictionary to %", path).postln;
			allIPs.writeArchive(path)
		});
	}

	*clearAllIPs {
		allIPs = IdentityDictionary();
	}

	*loadAllIPs {|path|
		if(File.exists(path), {
			var obj = Object.readArchive(path);
			format("Loading name/IP dictionary from %...", path).post;
			if(obj.isKindOf(IdentityDictionary), {allIPs = obj; " success".postln}, {" failed".postln});
			"allIPs :".postln; allIPs.postln;
			format("Total number of IPs: %", allIPs.size).postln;
		});
	}

	findPython {
		if(("which" + pythonPath).unixCmdGetStdOut.size > 0, {
			pythonFound = true
		}, {
			//macOS: add homebrew path
			"PATH".setenv("PATH".getenv++":/usr/local/bin");
			if(("which" + pythonPath).unixCmdGetStdOut.size > 0, {
				pythonFound = true
			}, {
				Error("Couldn't find" + pythonPath).throw
			});
		});
	}

	getIPfromName {|name|
		var result;
		// "name: ".post; name.postln;
		// "allIPs[name.asSymbol]: ".post; allIPs[name.asSymbol].postln;
		// "allIPs: ".post; allIPs.postln;
		if(allIPs.notNil, {
			result = allIPs[name.asSymbol];
			result ?? {format("IP for % not found in the dictionary", name).postln};
		});
		result !? {format("name: %, ip:", name, result).postln};
		^result;
	}

	initOpenBCI {|argPort, argBaudrate, argDataAction, argReplyAction, argInitAction|
		port= SerialPort(argPort ? "/dev/tty.OpenBCI-DM00DRM0", argBaudrate, crtscts:true);
		CmdPeriod.doOnce({port.close});

		//--default actions
		dataAction= argDataAction;
		replyAction= argReplyAction ? {|reply| reply.postln};
		initAction= argInitAction;

		//--startup
		("% starting...").format(this.class.name).postln;
		this.softReset;

		//--read loop
		task= Routine({this.prTask}).play(SystemClock);

		//--free on shutdown
		freeFunc = {this.free};
		ShutDown.add(freeFunc);
	}

	initOpenBCIwifi {|argName, argDataAction, argReplyAction, argInitAction, argLatency|
		wifi = true;
		msgList = List();
		if(pythonFound.not, {this.findPython});
		name = argName;

		// CmdPeriod.doOnce({port.close});

		//--default actions
		dataAction= argDataAction;
		replyAction= argReplyAction ? {|reply| reply.postln};
		initAction= argInitAction;

		//osc preparation
		thisOscPrefix = globalOscPrefix;
		thisOscPath = thisOscPrefix ++ "/" ++ name;

		//latency
		latency = argLatency;

		//--startup
		this.startPython;

		//--free on shutdown
		freeFunc = {this.free};
		ShutDown.add(freeFunc);
	}

	startPython {
		this.startResponders;
		// cmd = pythonPath + scriptPath + "--host localhost" + "--port" + NetAddr.langPort + "--address" + thisOscPath;
		cmd = format("% -u  % --host localhost --port % --address % --latency %", pythonPath, scriptPath, NetAddr.langPort, thisOscPath, latency);
		"cmd: ".post; cmd.postln;
		if(runInTerminal, { //on macos
			try {
				cmd.runInTerminal;
				// runInTerminalSucceeded = true;
			} {
				pid = cmd.unixCmd({this.freeResponders}); //free responders on exit
			};
		}, {
			pid = cmd.unixCmd({this.freeResponders}); //free responders on exit
		});
	}

	startResponders {
		this.freeResponders;
		responders = [
			OSCFunc({|msg|
				pythonPort = msg[1];
				pythonNetAddr = NetAddr("localhost", pythonPort);
				//process list
				if(msgList.size > 0, {
					msgList.size.do({this.sendMsg(*msgList.pop)});
				});
			}, thisOscPath ++ '/receivePort'),

			OSCFunc({|msg|
				isConnected = msg[1].asBoolean;
				this.changed(\connected, isConnected);
				format("% is %", name, isConnected.if({"connected"}, {"disconnected"})).postln;
			}, thisOscPath ++ '/connected'),

			OSCFunc({|msg|
				isStreaming = msg[1].asBoolean;
				this.changed(\streaming, isStreaming);
				format("%: streaming %", name, isStreaming.if({"started"}, {"stopped"})).postln;
			}, thisOscPath ++ '/streaming'),

			OSCFunc({|msg|
				var message = msg[1..];
				this.changed(\message, message);
				if(postMessages, {
					format("%:", name).scatArgs(*message).postln;
				});
			}, thisOscPath ++ '/message'),

			OSCFunc({|msg| dataAction.(msg[1..])}, thisOscPath),
		]
	}

	freeResponders {
		// responders.do(_.free);
		responders.do({|resp| resp.free});
		responders = [];
	}

	close {
		this.stop;
		// "OpenBCI: running close function".warn;
		ShutDown.remove(freeFunc);
		if(wifi, {
			"OpenBCI: shutting down Python bridge".postln;
			if(pid.notNil, {
				// ("kill" + pid).unixCmd;
				thisProcess.platform.killProcessByID(pid);
			}, {
				this.sendMsg('/quit');
			});
			this.freeResponders;
		}, {
			task.stop;
			port.close;
		});
	}

	free {
		this.close
	}

	put {|byte|
		if(wifi, {
			this.sendMsg('/send_command', byte.asString) //this needs fixing for sending multiple msgs
		}, {
			port.put(byte)
		})
	}
	putAll {|bytes|
		if(wifi, {
			this.sendMsg('/send_command', bytes.asString)
		}, {
			port.putAll(bytes)
		})
	}
	sendMsg {|...msgs|
		if(pythonNetAddr.notNil, {
			pythonNetAddr.sendMsg(*msgs)
		}, {
			// "pythonNetAddr not ready".warn;
			// messages are queued
			msgList.add(msgs);
		})
	}

	//--commands
	off {|channel= 1|  //Turn Channels OFF
		channel.asArray.do{|c|
			if(c>=1 and:{c<=this.class.numChannels}, {
				switch(c,
					1, {this.put($1)},
					2, {this.put($2)},
					3, {this.put($3)},
					4, {this.put($4)},
					5, {this.put($5)},
					6, {this.put($6)},
					7, {this.put($7)},
					8, {this.put($8)},
					9, {this.put($q)},
					10, {this.put($w)},
					11, {this.put($e)},
					12, {this.put($r)},
					13, {this.put($t)},
					14, {this.put($y)},
					15, {this.put($u)},
					16, {this.put($i)}
				);
			}, {
				"channel % not in the range 1-%".format(c, this.class.numChannels).warn;
			});
		};
	}
	on {|channel= 1|  //Turn Channels ON
		channel.asArray.do{|c|
			if(c>=1 and:{c<=this.class.numChannels}, {
				switch(c,
					1, {this.put($!)},
					2, {this.put($@)},
					3, {this.put($#)},
					4, {this.put($$)},
					5, {this.put($%)},
					6, {this.put($^)},
					7, {this.put($&)},
					8, {this.put($*)},
					9, {this.put($Q)},
					10, {this.put($W)},
					11, {this.put($E)},
					12, {this.put($R)},
					13, {this.put($T)},
					14, {this.put($Y)},
					15, {this.put($U)},
					16, {this.put($I)}
				);
			}, {
				"channel % not in the range 1-%".format(c, this.class.numChannels).warn;
			});
		};
	}

	startLogging {|time= '5MIN'|  //initiate sd card data logging for specified time
		switch(time,
			'5MIN', {this.put($A)},
			'15MIN', {this.put($S)},
			'30MIN', {this.put($F)},
			'1HR', {this.put($G)},
			'2HR', {this.put($H)},
			'4HR', {this.put($J)},
			'12HR', {this.put($K)},
			'24HR', {this.put($L)},
			'14SEC', {this.put($a)},
			{"time % not recognised".format(time).warn}
		);
	}
	stopLogging {  //stop logging data and close sd file
		this.put($j);
	}

	connect {|argIP, sampleRate = 0, maxPacketsToSkip=20, latency=10000, timeout=3, attempts=5, useTCP=true| //ip is optional - provide if service discovery not desired
		if(wifi, {
			ip = argIP ? this.getIPfromName(name);
			// sampleRate ?? {sampleRate == 250};
			this.sendMsg('/connect', ip ? name, sampleRate, maxPacketsToSkip, latency, timeout, attempts, useTCP);
			format("connecting to %...", name).postln;
		}, {
			".connect method is used only in wifi mode!".warn;
		})
	}

	start { |bufferOrBus| //start streaming data; optionally set server bus or buffer directly; make sure the bus has the proper number of channels! (counter + eeg_channels (4/8/16) + accelerometer (3)
		if(wifi, {
			if(isConnected, {
				if(bufferOrBus.isNil, {
					this.sendMsg('/start_streaming'); //standard streaming
				}, {
					var msg, num, startFrame;
					if(bufferOrBus.isKindOf(Bus), {
						num = bufferOrBus.index;
						msg = '/c_setn';
						this.sendMsg('/start_streaming', bufferOrBus.server.addr.ip, bufferOrBus.server.addr.port, msg, num); //direct to scsynth streaming
					}, {//assume buffer
						num = bufferOrBus.bufnum;
						msg = '/b_setn';
						startFrame = 0;
						this.sendMsg('/start_streaming', bufferOrBus.server.addr.ip, bufferOrBus.server.addr.port, msg, num, startFrame); //direct to scsynth streaming
					});
				});
			}, {
				"The board seems not to be connected, not starting".warn;
			});
		}, {
			this.put($b);
		})
	}
	stop {  //stop streaming data
		if(wifi, {
			this.sendMsg('/stop_streaming');
		}, {
			this.put($s);
		})
	}
	query {
		this.put($?);  //query register settings
	}
	softReset {
		this.put($v);  //soft reset for the board peripherals
	}

	attachWifi {
		this.put(${);
	}
	removeWifi {
		this.put($});
	}
	getWifiStatus {
		this.put($:);
	}
	softResetWifi {
		this.put($;);
	}

	prTask {^this.subclassResponsibility(thisMethod)}
}
