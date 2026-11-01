from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI(title="GenAnime StoryStudio Pro")

# --- Data Models ---
class StoryRequest(BaseModel):
    prompt: str
    genre: str = "Sci-Fi / Action"
    mood: str = "Epic"

# --- HTML / CSS Frontend UI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenAnime StoryStudio Pro</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Outfit', sans-serif; background-color: #0f1016; color: #f8fafc; }
    </style>
</head>
<body class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-[#181a26] border-b border-gray-800 py-4 px-8 flex justify-between items-center">
        <h1 class="text-2xl font-ext500 font-bold bg-gradient-to-r from-pink-500 to-indigo-500 bg-clip-text text-transparent">
            ✨ GenAnime StoryStudio Pro
        </h1>
        <span class="text-xs bg-indigo-900/50 text-indigo-300 px-3 py-1 rounded-full border border-indigo-700/50">Codespaces Ready</span>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-6xl w-full mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Control Panel -->
        <div class="bg-[#181a26] border border-gray-800 rounded-2xl p-6 flex flex-col gap-4 h-fit">
            <h2 class="text-lg font-semibold text-gray-200">🎬 Project Settings</h2>
            
            <div>
                <label class="text-xs text-gray-400 font-medium">Story Prompt / Core Idea</label>
                <textarea id="promptInput" rows="4" class="w-full mt-1 bg-[#12131c] border border-gray-700 rounded-xl p-3 text-sm focus:outline-none focus:border-pink-500 text-gray-200" placeholder="e.g., A lonely mech pilot discovers a hidden garden on a ruined space station..."></textarea>
            </div>

            <div>
                <label class="text-xs text-gray-400 font-medium">Anime Genre Style</label>
                <select id="genreSelect" class="w-full mt-1 bg-[#12131c] border border-gray-700 rounded-xl p-3 text-sm focus:outline-none focus:border-pink-500 text-gray-200">
                    <option>Cyberpunk / Action</option>
                    <option>Makoto Shinkai Cinematic Drama</option>
                    <option>Dark Fantasy / Shonen</option>
                    <option>Slice of Life / Cozy</option>
                </select>
            </div>

            <button onclick="generateStory()" class="mt-2 w-full bg-gradient-to-r from-pink-600 to-indigo-600 hover:from-pink-500 hover:to-indigo-500 font-semibold py-3 rounded-xl transition duration-200 shadow-lg shadow-pink-600/20 cursor-pointer">
                Generate Anime Production
            </button>
        </div>

        <!-- Output Display Area -->
        <div class="md:col-span-2 flex flex-col gap-6">
            <div id="loading" class="hidden bg-[#181a26] border border-gray-800 rounded-2xl p-12 text-center text-gray-400">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-pink-500 border-t-transparent mb-3"></div>
                <p>Generating storyboard, character keyframes, and detailed anime script...</p>
            </div>

            <div id="resultContainer" class="flex flex-col gap-6">
                <div class="bg-[#181a26] border border-gray-800 rounded-2xl p-6 text-center text-gray-500">
                    <p class="text-lg">Your generated anime script and storyboard frames will appear here.</p>
                </div>
            </div>
        </div>
    </main>

    <script>
        async function generateStory() {
            const prompt = document.getElementById('promptInput').value.trim();
            const genre = document.getElementById('genreSelect').value;
            const loading = document.getElementById('loading');
            const container = document.getElementById('resultContainer');

            if (!prompt) {
                alert("Please enter a story prompt!");
                return;
            }

            loading.classList.remove('hidden');
            container.innerHTML = '';

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, genre })
                });
                const data = await response.json();
                
                loading.classList.add('hidden');
                
                let html = `
                    <div class="bg-[#181a26] border border-gray-800 rounded-2xl p-6">
                        <h3 class="text-xl font-bold text-pink-400 mb-2">${data.title}</h3>
                        <p class="text-xs text-indigo-300 font-mono mb-4">Genre: ${data.genre} | Est. Runtime: 3 min</p>
                        <div class="space-y-4">
                `;

                data.scenes.forEach((scene, index) => {
                    html += `
                        <div class="bg-[#12131c] border border-gray-800/80 rounded-xl p-4 flex flex-col md:flex-row gap-4 items-center">
                            <div class="w-full md:w-40 h-28 bg-gray-900 rounded-lg flex items-center justify-center border border-gray-800 text-xs text-gray-500 relative overflow-hidden group">
                                <div class="absolute inset-0 bg-gradient-to-tr from-pink-900/20 to-indigo-900/20"></div>
                                <span class="z-10 font-mono text-pink-300">Frame #${index + 1}</span>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-sm font-semibold text-gray-200">Scene ${index + 1}: ${scene.setting}</h4>
                                <p class="text-xs text-gray-400 mt-1"><strong>Action:</strong> ${scene.action}</p>
                                <p class="text-xs text-indigo-200 mt-1 italic">"${scene.dialogue}"</p>
                                <div class="mt-2 text-[10px] bg-gray-800/60 text-gray-400 px-2 py-1 rounded inline-block font-mono">Camera: ${scene.camera}</div>
                            </div>
                        </div>
                    `;
                });

                html += `</div></div>`;
                container.innerHTML = html;

            } catch (err) {
                loading.classList.add('hidden');
                alert("An error occurred while generating the script.");
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_UI

@app.post("/generate")
async def generate_story_endpoint(req: StoryRequest):
    # Simulated high-detail anime script generation logic
    # In your full Codespaces environment, you can hook this up to an LLM API or local model pipeline.
    titles = [
        f"Echoes of {req.prompt.split()[0].capitalize()}",
        f"The Last Chronicle: {req.genre.split('/')[0].strip()}",
        "Beyond the Neon Horizon",
        "Chronicles of the Astral Gate"
    ]
    
    settings = ["Neon-lit Alleyway, Rain", "Abandoned Orbital Station, Glowing Terminal", "Lush Floating Island at Sunset", "Underground Tech Citadel"]
    actions = [
        "Protagonist adjusts their visor as warning sirens flash in crimson tones.",
        "A sudden energy surge illuminates the dust particles floating in zero-G.",
        "The wind blows through the tall cyber-grass as a distant ship breaks orbit.",
        "Holographic screens flicker to life, mapping out an unknown coordinates grid."
    ]
    dialogues = [
        "We're running out of time... Can you bypass the main firewall?",
        "Look at the stars. They look different from up here.",
        "I didn't come this far just to turn back now.",
        "Initiating final sequence. Hold onto something!"
    ]
    cameras = [
        "Dynamic Low Angle Shot -> Close-up on eyes",
        "Wide Cinematic Pan -> Slow Zoom",
        "Over-the-shoulder tracking shot",
        "Rapid Action Cut -> Dutch Angle"
    ]

    selected_title = random.choice(titles)
    scenes = []
    for i in range(3):
        scenes.append({
            "setting": random.choice(settings),
            "action": random.choice(actions),
            "dialogue": random.choice(dialogues),
            "camera": random.choice(cameras)
        })

    return {
        "title": selected_title,
        "genre": req.genre,
        "scenes": scenes
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)