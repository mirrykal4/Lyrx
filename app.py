# app.py
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return "Lyrics API is running! Use /lyrics?song_name=your_song to get lyrics."

@app.route('/lyrics', methods=['GET'])
def get_lyrics():
    song_name = request.args.get('song_name')
    if not song_name:
        return jsonify({"status": "error", "message": "Please provide a song name."}), 400

    # **इस हिस्से को LyricsMint के HTML स्ट्रक्चर के अनुसार बदलें!**
    # उदाहरण के लिए URL बनाना (आपको सही URL पैटर्न खोजना होगा)
    formatted_song_name = song_name.replace(' ', '-').replace("'", "").lower()
    lyricsmint_url = f"https://www.lyricsmint.com/{formatted_song_name}-lyrics.html" # यह एक अनुमानित पैटर्न है

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(lyricsmint_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # **यहां आपको LyricsMint के HTML को देखकर सही div/class खोजना होगा**
        # उदाहरण: lyrics एक विशिष्ट div के अंदर हो सकते हैं
        lyrics_container = soup.find('div', class_='text-center') # यह बदल सकता है

        if lyrics_container:
            lyrics = lyrics_container.get_text(separator="\n", strip=True)
            # कुछ अतिरिक्त टेक्स्ट जैसे "Lyrics:", "Singer:", "Movie:" आदि हटाने के लिए
            # आप regex या string methods का उपयोग कर सकते हैं.
            # उदाहरण के लिए, सिर्फ लिरिक्स वाला हिस्सा रखने के लिए:
            # if "Lyrics:" in lyrics:
            #    lyrics = lyrics.split("Lyrics:", 1)[1].strip()

            return jsonify({
                "status": "success",
                "song_name": song_name,
                "source_url": lyricsmint_url,
                "lyrics": lyrics
            })
        else:
            return jsonify({"status": "error", "message": "Lyrics content not found on the page. HTML structure might have changed or song not found."}), 404

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return jsonify({"status": "error", "message": "Song not found on LyricsMint. Please check the song name."}), 404
        else:
            return jsonify({"status": "error", "message": f"HTTP error occurred: {e}"}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({"status": "error", "message": "Could not connect to LyricsMint. Please check your internet connection or the website status."}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True) # Production में debug=False करें
