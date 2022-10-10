import {
    api_ip_address,
    metrics_url,
    metrics_token,
    metrics_org,
    metrics_bucket,
    instance,
} from './env.js';

import {InfluxDB, Point} from '@influxdata/influxdb-client';
import { Manager } from 'socket.io-client';

let detection_accumulation = {};

console.log('metrics_url=' + metrics_url);
const metrics_prefix = "frontend_service";

const headers = {
    "Authorization": `Bearer ${metrics_token}`
};

// const headers = {
//     "Authorization": "Basic " + btoa(`${metrics_username}:${metrics_password}`)
// };

const writeOptions = {
    batchSize: 5,
    'instance': instance,
    flushInterval: 0,
    maxRetries: 10,
    headers,
};

const influxDbOptions = {
    "url": metrics_url,
    "token": metrics_token,
    "transportOptions": {
        "mode": "no-cors",
        headers,
    },
    headers,
    "writeOptions": writeOptions
};

const influxDb = new InfluxDB(influxDbOptions);

const writeApi = influxDb.getWriteApi(metrics_org, metrics_bucket, 'ns', writeOptions);

const writeSimpleMetric = (prefix, field, value = 1, tags = {}) => {
    const point = new Point(`${metrics_prefix}_${prefix}`);

    for (const key in tags) {
        const value = tags[key];
        point.tag(key, value);
    }
    point.intField(field, value);
    writeApi.writePoint(point);
    // console.log('Sent a metric');
};

// 'ws://${API_IP_ADDRESS}'
const manager = new Manager(api_ip_address, {
    reconnectionDelayMax: 500
});

const socket = manager.socket('/', {
});

socket.on('connect', () => {
    const engine = socket.io.engine;
    console.log(`SIO: Connected! id='${socket.id}' transport='${engine.transport.name}'`);

    engine.once('upgrade', () => {
        console.log(`SIO: changed transport='${engine.transport.name}'`);
    });

    engine.on('close', (reason) => {
        console.log(`SIO: Disconnected! ${reason}`);
        writeSimpleMetric('sio', 'disconnection');
    });
});

document.getElementById('send-ping').addEventListener('click', function(event) {
    console.log('Sending a ping');
    event.preventDefault();
    socket.emit('ping');

    writeSimpleMetric('sio', 'ping');
});

socket.on('pong', () => {
    console.log('Received a pong');
    alert('Received a pong');

    writeSimpleMetric('sio', 'pong');
});

socket.on('detection', (data) => {
    console.log('Received a detection! ' + JSON.stringify(data));

    // --- Update detections and totals ---
    let total_counts = {};
    const areas = [
        "detections",
        "detection-totals"
    ];
    for (const area_index in areas) {
        const area = areas[area_index];
        const area_metric = area.replace("-", "_");
        const ul = document.getElementById(area);
        ul.innerHTML = '';
        total_counts[area] = 0;
        for (const code in data[area]) {
            const value = data[area][code];

            total_counts[area] = total_counts[area] + parseInt(value);
            const key_value = `${code}=${value}`;

            const li = document.createElement('li');
            li.appendChild(document.createTextNode(key_value));
            ul.appendChild(li);

            writeSimpleMetric('detections', `type_${area_metric}`, value, {'code': code});

            // accumulation comes from detections
            if (area === "detections") {
                if (!(code in detection_accumulation)) {
                    detection_accumulation[code] = 0;
                }
                detection_accumulation[code] += value;
            }
        }
        writeSimpleMetric('detections', `count_${area_metric}`, total_counts["accumulations"]);
    }

    // --- Update accumulations ---
    total_counts["accumulations"] = 0;
    const accumulations_ul = document.getElementById("detection-accumulation");
    accumulations_ul.innerHTML = '';
    for (const code in detection_accumulation) {
        const value = detection_accumulation[code];
        const key_value = `${code}=${value}`;

        const li = document.createElement('li');
        li.appendChild(document.createTextNode(key_value));
        accumulations_ul.appendChild(li);

        total_counts["accumulations"] += value;

        writeSimpleMetric("detections", 'type_accumulations', value, {'type': code});
    }
    writeSimpleMetric('detections', 'count_accumulations', total_counts["accumulations"]);

    // --- Log a point that we received data ---
    writeSimpleMetric('detections', 'received');
});
