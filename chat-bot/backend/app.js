const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());
app.use(cors());

app.set('json spaces', 2);

// List of random sentences
const randomSentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Life is what happens when you're busy making other plans.",
    "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "In the end, it's not the years in your life that count. It's the life in your years."
];

// POST endpoint to handle the request
app.post('/generate', (req, res) => {
    const { prompt } = req.body;

    if (!prompt) {
        return res.status(400).json({ error: 'Missing prompt field in the request body' });
    }

    // Generate a random sentence from the list
    const randomSentence = randomSentences[Math.floor(Math.random() * randomSentences.length)];

    // Respond with the random sentence
    res.json({ prompt, randomSentence });
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
