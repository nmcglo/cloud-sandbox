const express = require('express');
const amqp = require('amqplib/callback_api');

const app = express();
app.use(express.json());

var request_id = 0;

const RABBITMQ_SERVER = 'amqp://user:password@rabbitmq.cloud-testing.svc.cluster.local:5672';

app.post('/request_compute', (req, res) => {

    const payload = {
        "message": req.body,
        "request_id": request_id++
    };

    const message = JSON.stringify(payload);

    amqp.connect(RABBITMQ_SERVER, function(error0, connection) {
        if (error0) {
            console.error('Failed to connect to RabbitMQ:', error0);
            return res.status(500).send('Error processing request');
        }

        connection.createChannel(function(error1, channel) {
            if (error1) {
                console.error('Failed to create channel:', error1);
                return res.status(500).send('Error processing request');
            }

            const queue = 'compute-work';

            channel.assertQueue(queue, {
                durable: false
            });

            channel.sendToQueue(queue, Buffer.from(message));
            console.log(" [x] Sent %s", message);

            res.status(200).json({
                "message": "Request sent to worker queue",
                "request_id": payload.request_id
            });
        });

        setTimeout(function() {
            connection.close();
        }, 500);
    });
});

process.on('SIGTERM', () => {
    server.close(() => {
      console.log('Process terminated')
      process.exit(0);
    });
  });

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Node.js server listening on port ${PORT}`);
});
