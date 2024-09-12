const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

const accept_null_origin = false;
const allowed_origins = ["*"];

const corsOptions = {
    origin: (origin, callback) => {
        if (accept_null_origin && !origin) { // curl doesn't add an origin header by default - we want to accept that by default
            callback(null, true);
        }
        else if (allowed_origins.some(allowedOrigin => {
            if (allowedOrigin.includes('*')) {
                const regex = new RegExp(`^${allowedOrigin.replace(/\*/g, '.*')}$`);
                return regex.test(origin);
            }
            return allowedOrigin === origin;
        })) {
            callback(null, true);
        } else {
            logger.warn(`Request from origin: '${origin}' blocked due to CORS configuration`);
            callback(new CorsError("Request blocked due to CORS configuration"));
        }
    },
    credentials: false,
    allowedHeaders: ['Content-Type', 'Authorization'],
}

app.use(cors(corsOptions));

app.set('json spaces', 2);

// List of random sentences
const randomSentences = [
    "The quick brown fox jumps over the lazy dog.",
    "Life is what happens when you're busy making other plans.",
    "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "In the end, it's not the years in your life that count. It's the life in your years."
];


function authenticateToken(req, res, next) {
    req.userID = null;
    req.isAdmin = false;

    const authHeader = req.headers['authorization'];
    let token = authHeader && authHeader.split(' ')[1]


    if (token == null) {
        req.userID = null;
        return res.status(403).json({message: "no token provided"});
    }
    else {
        if (token === "testtoken") {
            next();
        } else {
            return res.status(403).json({message:`invalid token: ${token}`});
        }
    }
}

app.use(authenticateToken);

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
