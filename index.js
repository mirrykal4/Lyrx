const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

async function getLyricsGenius(query) {
  try {
    const searchUrl = `https://genius.com/api/search/multi?per_page=1&q=${encodeURIComponent(query)}`;
    const searchRes = await axios.get(searchUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      timeout: 7000
    });

    const songPath = searchRes.data.response.sections[0].hits[0].result.path;
    const songUrl = `https://genius.com${songPath}`;
    const pageRes = await axios.get(songUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0' },
      timeout: 7000
    });

    const $ = cheerio.load(pageRes.data);
    let lyrics = '';
    $('[data-lyrics-container="true"]').each((i, el) => {
      lyrics += $(el).text() + '\n';
    });

    return lyrics.trim() || 'Lyrics not found.';
  } catch (err) {
    console.error("Error fetching lyrics:", err.message);
    return 'Lyrics not found or scraping failed.';
  }
}

// Serve static index.html
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// API endpoint
app.get('/lyrics', async (req, res) => {
  const { query } = req.query;
  if (!query) return res.status(400).send('Missing query.');

  const lyrics = await getLyricsGenius(query);
  res.json({ lyrics });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
