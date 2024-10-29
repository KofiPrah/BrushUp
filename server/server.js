// src/server.js
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

const app = express();
const PORT = 5000;


app.use(cors());
app.use(express.json());

// Static file serving for uploaded images
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// In-memory user data for demonstration purposes
let users = [
  {
    id: 1,
    username: 'JaneDoe',
    bio: 'Artist and Designer',
    headerImage: '',
    profileImage: '',
    artworks: [],
  },
];

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  },
});

const upload = multer({ storage: storage });

// Fetch user data
app.get('/api/user/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  const user = users.find((u) => u.id === userId);

  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }

  res.json(user);
});

// Upload header or profile image
app.post('/api/user/:id/upload', upload.single('image'), (req, res) => {
  const userId = parseInt(req.params.id);
  const user = users.find((u) => u.id === userId);

  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }

  if (!req.file) {
    return res.status(400).json({ message: 'No file uploaded.' });
  }

  if (req.body.type === 'header') {
    user.headerImage = `http://localhost:${PORT}/uploads/${req.file.filename}`;
  } else if (req.body.type === 'profile') {
    user.profileImage = `http://localhost:${PORT}/uploads/${req.file.filename}`;
  }

  res.json({ message: 'Image uploaded successfully!', user });
});

// Upload artwork
app.post('/api/artworks', upload.single('image'), (req, res) => {
  const { title, userId } = req.body;
  const user = users.find((u) => u.id === parseInt(userId));

  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }

  if (!req.file) {
    return res.status(400).json({ message: 'No file uploaded.' });
  }

  const newArtwork = {
    id: user.artworks.length + 1,
    title: title,
    imageUrl: `http://localhost:${PORT}/uploads/${req.file.filename}`,
  };

  user.artworks.push(newArtwork);

  res.json({ message: 'Artwork uploaded successfully!', artwork: newArtwork, user });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});