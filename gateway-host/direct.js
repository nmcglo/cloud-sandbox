const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

app.post('/request_compute', async (req, res) => {
    try {
        const response = await axios.post('http://compute-dummy-svc.cloud-testing.svc.cluster.local/compute', req.body);
        
        res.json(response.data);
    } catch (error) {
        console.error('Error communicating with compute-dummy:', error);
        res.status(500).send('Error processing request');
    }
});

process.on('SIGTERM', () => {
    server.close(() => {
      console.log('Process terminated')
      process.exit(0);
    });
  });

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Node.js server listening on port ${PORT}`);
});
