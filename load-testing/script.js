import {
	INTERVAL,
	CHUNK_SIZE,
	TAG_END_OF_SENTENCE,
	WEBSOCKET_CONFIGURATION,
	LOGGER
} from './constants.js';

import http from 'k6/http';
import ws from 'k6/ws';
import { sleep, fail } from 'k6';
import { Trend } from 'k6/metrics';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from "https://jslib.k6.io/k6-summary/0.0.1/index.js";

const rtfMetrics = new Trend('RTF');
const audioMetrics = new Trend('Audio');
const connectionPhase = new Trend('Phase_1_Connect_to_server');
const transcriptionPhase = new Trend('Phase_2_Audio_transcription');
const disconnectionPhase = new Trend('Phase_3_Disconnect_from_server');

const TOTAL_NUMBER_OF_VIRTUAL_USERS_TO_SPAWN = 1
const TOTAL_NUMBER_OF_ITERATIONS_TO_SEND = 1

export const options = {
	vus: TOTAL_NUMBER_OF_VIRTUAL_USERS_TO_SPAWN,
	iterations: TOTAL_NUMBER_OF_ITERATIONS_TO_SEND,
};

let START_TIME;
let END_OF_CONNECTION_TEST;
let START_OF_TRANSCRIPTION;
let END_OF_TRANSCRIPTION;
let END_CLOSING;

let audio_hashmap = {
	SHORT: "short_duration_audio",
	MEDIUM: "medium_duration_audio",
	LONG: "long_duration_audio"
}

if (!(`${__ENV.AUDIO_DURATION}` in audio_hashmap)) {
	fail('AUDIO_DURATION environmental variable must be either SHORT, MEDIUM, or LONG');
}

const binFile = open(`./audio/${audio_hashmap[__ENV.AUDIO_DURATION]}.wav`, 'b');
const binMeta = open(`./audio/${audio_hashmap[__ENV.AUDIO_DURATION]}.json`);
const binMetaObj = JSON.parse(binMeta)

export default function () {
	LOGGER(`VU ${__VU}`, `LOAD TEST STARTED FOR VU ${__VU}`)
	START_TIME = new Date();
	const url = WEBSOCKET_CONFIGURATION.server + '?' + WEBSOCKET_CONFIGURATION.contentType + "&model=english";
	const res = ws.connect(url, null, function (socket) {
		socket.on('open', function (e) {
			LOGGER(`VU ${__VU}`, `VU ${__VU} CONNECTED TO SERVER`)
			START_OF_TRANSCRIPTION = new Date();
			const f = http.file(binFile, 'audio/wav');
			var blob = f.data
			for (var i = 0; i < blob.length; i+=CHUNK_SIZE) {
				if(i + CHUNK_SIZE >= blob.length) {
					if (i < blob.length) {
						LOGGER(`VU ${__VU}`, `SENT ${blob.length - i} BYTES OF DATA`)
						socket.sendBinary(binFile.slice(i, blob.length))
					}
					break
				}
				LOGGER(`VU ${__VU}`, `SENT ${CHUNK_SIZE} BYTES OF DATA`)
				socket.sendBinary(binFile.slice(i, i+CHUNK_SIZE))
				sleep(INTERVAL)
			}
			socket.send(TAG_END_OF_SENTENCE)
			END_OF_TRANSCRIPTION = new Date();
		});
		socket.on('message', function(message) {
			const response = JSON.parse(message)
			if (response.status === 0) {
				if ("result" in response) {
					const trans = response["result"]['hypotheses'][0]['transcript']
					if ("final" in response["result"]) {
						LOGGER(`VU ${__VU}`, `TRANSCRIPT "${trans}"`)
					}
					else {
						let print_trans = trans
						if (print_trans.length > 80) {
							print_trans = `... ${print_trans.substring(-79, print_trans.length)}`
						}
						LOGGER(`VU ${__VU}`, `TRANSCRIPT "${print_trans}"`)
					}
				}
			}
		});
		socket.on('close', function(message) {
			LOGGER(`VU ${__VU}`, `VU ${__VU} DISCONNECTED FROM SERVER`)
			const END_TIME = new Date();
			const DECODING_DURATION = END_TIME - START_TIME
			const RTF = (DECODING_DURATION/1000) / parseInt(binMetaObj["DURATION"])
			LOGGER(`VU ${__VU}`, `CALCULATED RTF: ${RTF.toFixed(3)} per second of recorded audio`)
			rtfMetrics.add(RTF);
			audioMetrics.add(parseInt(binMetaObj["DURATION"]*1000));
		});
	});
	LOGGER(`VU ${__VU}`, `LOAD TEST COMPLETED FOR VU ${__VU}`)
	END_CLOSING = new Date();
	connectionPhase.add(START_OF_TRANSCRIPTION-START_TIME);
	transcriptionPhase.add(END_OF_TRANSCRIPTION-START_OF_TRANSCRIPTION);
	disconnectionPhase.add(END_CLOSING-END_OF_TRANSCRIPTION);
}

export function handleSummary(data) {
  return {
    "reports/summary.html": htmlReport(data),
    stdout: "\n" + textSummary(data, { indent: " ", enableColors: true }) + "\n\n",
  };
}
