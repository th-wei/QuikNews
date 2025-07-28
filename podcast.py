import news
import os
import http.server
import threading
import socketserver
from playsound import playsound

from podcastfy.client import generate_podcast
from IPython.display import Audio, display

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

def embed_audio(audio_file):
	"""
	Embeds an audio file in the notebook, making it playable.

	Args:
		audio_file (str): Path to the audio file.
	"""
	try:
		display(Audio(audio_file))
		print(f"Audio player embedded for: {audio_file}")
	except Exception as e:
		print(f"Error embedding audio: {str(e)}")
		
# Start HTTP server in background
def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}/output.txt")
        httpd.serve_forever()

# Define a custom conversation config for a tech debate podcast
podcast_config = {
    'conversation_style': ['Engaging', 'Fast-paced', 'Enthusiastic', 'Educational'], 
    'roles_person1': 'Tech Business Thought Leader', 
    'roles_person2': 'Tech and Business Economist', 
    'dialogue_structure': ['Topic Introduction', 'Summary of Key Points', 'Discussions'], 
    'podcast_name': 'Daily Metis News', 
    'podcast_tagline': 'Keep up with Metis on tech and business', 
    'output_language': 'English', 
    'user_instructions': 'Make it concise like the morning news', 
    'engagement_techniques': ['analysis', 'analogies'], 
    'creativity': 0.75
}

def generate_audio():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    audio_file = generate_podcast(urls=["http://localhost:8000/output.txt"],
                                    llm_model_name="gemini-2.5-pro",
								    tts_model='elevenlabs',
								    conversation_config=podcast_config)
    embed_audio(audio_file)


if __name__ == "__main__":
	news.create_podcast_content()
	generate_audio()
	playsound("./data/audio/podcast_365e5e199fc841dba100f8a94ce74a1f.mp3")
    