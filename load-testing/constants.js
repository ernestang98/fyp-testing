var INTERVAL = 0.25
var CHUNK_SIZE = 8000
var TAG_END_OF_SENTENCE = "EOS";
var DOCKER_HOST = "localhost"
var MINIKUBE_HOST = "10.103.10.61"
var CLOUD_K8 = "3.24.213.119"

var NORMAL_PORT="8010"
var CLOUD_PORT="30023"

var CLOUD_K8 = `${__ENV.HOST}`
var CLOUD_PORT=`${__ENV.PORT}`

var WEBSOCKET_CONFIGURATION = {
	server : `ws://${CLOUD_K8}:${CLOUD_PORT}/client/ws/speech`,
	serverStatus : `ws://${CLOUD_K8}:${CLOUD_PORT}/client/ws/status`,
	contentType: "content-type=audio/x-raw,+layout=(string)interleaved,+rate=(int)16000,+format=(string)S16LE,+channels=(int)1"
}

var LOGGER = function(label = null, process = null, status = null) {
	if (status == "WARN") console.warn(`${label} - ${process}`)
	else if (status == "ERROR") console.error(`${label} - ${process}`)
	else console.log(`${label} - ${process}`)
}

export {
	INTERVAL,
	CHUNK_SIZE,
	TAG_END_OF_SENTENCE,
	WEBSOCKET_CONFIGURATION,
	LOGGER,
}
