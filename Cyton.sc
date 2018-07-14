//--supercollider openbci cyton biosensing board (8-channels) communication

//http://docs.openbci.com/Hardware/03-Cyton_Data_Format
//http://docs.openbci.com/OpenBCI%20Software/04-OpenBCI_Cyton_SDK

//TODO: implement and test the different aux commands
//TODO: low pass filter
//TODO: notch filter (60/50 hz)
//TODO: test wifi shield commands
//TODO: test Daisy commands

Cyton : OpenBCI {
	classvar <numChannels= 8;

	//--commands
	testGnd {  //Connect to internal GND (VDD - VSS)
		this.put($0);
	}
	test1AmpSlow {  //Connect to test signal 1xAmplitude, slow pulse
		this.put($-);
	}
	test1AmpFast {  //Connect to test signal 1xAmplitude, fast pulse
		this.put($=);
	}
	testDC {  //Connect to DC signal
		this.put($p);
	}
	test2AmpSlow {  //Connect to test signal 2xAmplitude, slow pulse
		this.put($[);
	}
	test2AmpFast {  //Connect to test signal 2xAmplitude, fast pulse
		this.put($]);
	}

	settings {|channel= 1, powerDown= 0, gain= 6, type= 0, bias= 1, srb2= 1, srb1= 0|
		if(channel>=1 and:{channel<=8}, {
			this.put($x);
			this.put(channel.asDigit);
			this.put(powerDown.clip(0, 1).asDigit);
			this.put(gain.clip(0, 6).asDigit);
			this.put(type.clip(0, 7).asDigit);
			this.put(bias.clip(0, 1).asDigit);
			this.put(srb2.clip(0, 1).asDigit);
			this.put(srb1.clip(0, 1).asDigit);
			this.put($X);
		}, {
			"channel % out of range".format(channel).warn;
		});
	}
	setDefaultChannelSettings {  //set all channels to default
		this.put($d);
	}
	getDefaultChannelSettings {  //get a report
		this.put($D);
	}
	impedance {|channel= 1, pchan= 0, nchan= 0|
		if(channel>=1 and:{channel<=8}, {
			this.put($z);
			this.put(channel.asDigit);
			this.put(pchan.clip(0, 1).asDigit);
			this.put(nchan.clip(0, 1).asDigit);
			this.put($Z);
		}, {
			"channel % out of range".format(channel).warn;
		});
	}

	timeStampingON {
		this.put($<);
	}
	timeStampingOFF {
		this.put($>);
	}
	getRadioChannel {  //Get Radio Channel Number
		this.putAll(Int8Array[0xF0, 0x00]);
	}
	setRadioChannel {|channel= 7|  //Set Radio System Channel Number
		this.putAll(Int8Array[0xF0, 0x01, channel.clip(1, 25)]);
	}
	setRadioHostChannel {|channel= 7, really= false|  //Set Host Radio Channel Override
		if(really, {  //extra safety
			this.putAll(Int8Array[0xF0, 0x02, channel.clip(1, 25)]);
		}, {
			"changing might break the wireless connection. really=true to override".warn;
		});
	}
	getRadioPollTime {  //Radio Get Poll Time
		this.putAll(Int8Array[0xF0, 0x03]);
	}
	setRadioPollTime {|time= 80|  //Radio Set Poll Time
		this.putAll(Int8Array[0xF0, 0x04, time.clip(0, 255)]);
	}
	setRadioHostBaudRate {|rate= 0, really= false|  //Radio Set HOST to Driver Baud Rate
		if(really, {  //extra safety
			switch(rate,
				0, {this.putAll(Int8Array[0xF0, 0x05])},  //Default - 115200
				1, {this.putAll(Int8Array[0xF0, 0x06])},  //High-Speed - 230400
				2, {this.putAll(Int8Array[0xF0, 0x0A])},  //Hyper-Speed - 921600
				{"rate % not recognised".format(rate).warn}
			);
		}, {
			"changing will break the serial connection. really=true to override".warn;
		});
	}
	getRadioSystemStatus {  //Radio System Status
		this.putAll(Int8Array[0xF0, 0x07]);
	}
	getSampleRate {  //get current sample rate
		this.putAll("~~");
	}
	setSampleRate {|rate= 6|  //set sample rate
		this.putAll("~"++rate.clip(0, 6));
		if(wifi, {
			if((rate<4), {
				"The Cyton with WiFi shield cannot stream data over 1000SPS".warn;
			});
		}, {
			if((rate<6), {
				"The Cyton with USB Dongle cannot and will not stream data over 250SPS".warn;
			});
		})
	}
	setSampleRateHz {|rate= 250|  //set sample rate
		var rateInt;
		rate.switch(
			250, {rateInt = 6},
			500, {rateInt = 5},
			1000, {rateInt = 4},
			2000, {rateInt = 3},
			4000, {rateInt = 2},
			8000, {rateInt = 1},
			16000, {rateInt = 0},
			{"Invalid sample rate. The valid rates (Hz) are 250, 500, 1000, 2000, 4000, 8000, 16000".warn}
		);
		rateInt !? {this.setSampleRate(rateInt)};
	}

	getBoardMode {  //get current board mode
		this.putAll("//");
	}
	setBoardMode {|mode= 0|  //set board mode
		this.putAll("/"++mode.clip(0, 4));
	}

	getVersion {  //get firmware version
		this.put($V);
	}

	//--private
	prTask {
		var last3= [0, 0, 0];
		var buffer= List(32);
		var state= 0;
		var reply, num, aux= (26..31);
		0.1.wait;
		inf.do{|i|
			var byte= port.read;
			//byte.postln;  //debug
			buffer.add(byte);
			switch(state,
				0, {
					if(byte==0xA0, {  //header
						if(buffer.size>1, {
							buffer= List(32);
							buffer.add(byte);
						});
						state= 1;
					}, {
						last3[i%3]= byte;
						if(last3==#[36, 36, 36], {  //eot $$$
							if(buffer[0]==65, {  //TODO remove this
								buffer= buffer.drop(32);
								//"temp fix applied".postln;  //debug
							});
							reply= "";
							(buffer.size-3).do{|i| reply= reply++buffer[i].asAscii};
							if(reply.contains("OpenBCI V3 8-16 channel"), {
								initAction.value(reply);
							});
							replyAction.value(reply);
							buffer= List(32);
						});
					});
				},
				1, {
					if(buffer.size>=32, {
						state= 2;
					});
				},
				2, {
					if(byte>=0xC0 and:{byte<=0xCF}, {  //check valid footer
						num= buffer[1];  //sample number
						data= Array.fill(numChannels, {|i|  //eight channels of 24bit data
							var msb= buffer[i*3+2];
							var pre= 0;
							if(msb&128>0, {
								pre= -0x01000000;
							});
							pre+(msb<<16)+(buffer[i*3+3]<<8)+buffer[i*3+4];
						});
						switch(byte,  //footer / stop byte
							0xC0, {  //accelerometer
								if(aux.any{|i| buffer[i]!=0}, {
									accel= Array.fill(3, {|i|  //three dimensions of 16bit data
										var msb= buffer[i*2+26];
										var pre= 0;
										if(msb&128>0, {
											pre= -0x010000;
										});
										pre+(msb<<8)+buffer[i*2+27];
									});
									accelAction.value(accel);
								});
							};
						);
						dataAction.value(num, data, buffer[aux], byte);
					}, {
						buffer.postln;
						("% read error").format(this.class.name).postln;
					});
					buffer= List(32);
					state= 0;
				}
			);
		};
	}
}

CytonDaisy : Cyton {
	classvar <numChannels= 16;
	settings {|channel= 1, powerDown= 0, gain= 6, type= 0, bias= 1, srb2= 1, srb1= 0|
		if(channel>=1 and:{channel<=16}, {
			this.put($x);
			switch(channel,
				9, {this.put($Q)},
				10, {this.put($W)},
				11, {this.put($E)},
				12, {this.put($R)},
				13, {this.put($T)},
				14, {this.put($Y)},
				15, {this.put($U)},
				16, {this.put($I)},
				{this.put(channel.asDigit)}
			);
			this.put(powerDown.clip(0, 1).asDigit);
			this.put(gain.clip(0, 6).asDigit);
			this.put(type.clip(0, 7).asDigit);
			this.put(bias.clip(0, 1).asDigit);
			this.put(srb2.clip(0, 1).asDigit);
			this.put(srb1.clip(0, 1).asDigit);
			this.put($X);
		}, {
			"channel % out of range".format(channel).warn;
		});
	}
	maximumChannelNumber {|channels= 16|
		switch(channels,
			8, {this.put($c)},
			16, {this.put($C)},
			{"channels can only be 8 or 16".warn}
		);
	}

	//--private
	prTask {  //TODO
		var last3= [0, 0, 0];
		var buffer= List(32);
		var state= 0;
	}
}
