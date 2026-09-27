# My agent: FitCoach AI

**One-liner**: A comprehensive conversational AI fitness coach that helps users calculate nutrition/macros, find nearby gyms, look up global exercises, log workouts to Firestore, generate visual workout graphics with Gemini 3.1 & Imagen, and run sandboxed Python calculations.

---

## Current Agent Capabilities & Integrated Tools

### 1. 🧮 Physiological & Macro Calculator
- **Tool**: `calculate_macros_and_zones(weight_kg, height_cm, age, gender, activity_level, goal)`
- **Module**: `app/fitness_calculator.py`
- **Capabilities**: Computes BMR (Mifflin-St Jeor formula), TDEE, goal-adjusted calorie targets (cut, bulk, maintain), macronutrient splits (Protein, Carbs, Fats), and 5 Heart Rate Training Zones (Karvonen formula).

### 2. 🗄️ Firestore Database & Workout Logger
- **Backend**: Default Firestore Database `(default)` in `us-central1` (Project: `qwiklabs-gcp-02-210a21fedfc2`).
- **Tools**:
  - `list_exercises()`: Retrieves all available exercise documents.
  - `get_exercise(name)`: Looks up detailed exercise info (muscle groups, equipment, instructions).
  - `add_exercise(name, category, muscle_group, equipment, instructions)`: Stores custom exercise entries in Firestore.
  - `log_user_workout(workout_name, duration_minutes, exercises_completed, notes)`: Logs completed workout sessions.
- **Module**: `app/firestore_tools.py`

### 3. 🎨 Visual Workout Card Generator
- **Storage**: Public Cloud Storage bucket `gs://fitcoach-ai-media-qwiklabs-gcp-02-210a21fedfc2`.
- **Tool**: `generate_workout_card_image(title, details)`
- **Module**: `app/image_tool.py`
- **Capabilities**: Generates sleek, dark-themed workout infographic PNG cards using PIL, uploads them to GCS, and returns public HTTPS image URLs.

### 4. 🌐 Wger Public Exercise Database API
- **API**: Wger Workout Manager Open API (`https://wger.de/api/v2/exerciseinfo/`).
- **Tool**: `search_public_exercise_database(term)`
- **Module**: `app/wger_tool.py`
- **Capabilities**: Queries global exercise definitions, target muscles, equipment, and categories without requiring API key authentication.

### 5. 🗺️ Google Maps & Places (New) Integration
- **APIs**: Geocoding API (`geocoding.googleapis.com`) & Places API New (`places.googleapis.com`).
- **Tools**:
  - `geocode_address(address)`: Converts addresses/cities into latitude & longitude coordinates.
  - `find_nearby_places(latitude, longitude, place_type, radius_meters)`: Uses Places API (New) REST endpoint (`/v1/places:searchNearby`) to discover nearby gyms, fitness centers, parks, or sports complexes with name, formatted address, and location.
- **Module**: `app/maps_tools.py`

### 6. 🖼️ Gemini 3.1 Flash Lite Image Generator & Playground Artifacts
- **Model**: `gemini-3.1-flash-lite-image` in `global` region.
- **Tool**: `generate_fitness_illustration(prompt, tool_context)`
- **Module**: `app/gemini_image_tool.py`
- **Capabilities**: Generates high-quality exercise technique illustrations. Saves the generated image to the ADK `ToolContext` (`save_artifact`) for rendering in the Playground UI Artifacts panel, and uploads the image bytes directly to public GCS.

### 7. 🐍 Agent Engine Sandbox Code Execution
- **Executor**: `AgentEngineSandboxCodeExecutor`
- **Runtime ID**: `projects/112281838041/locations/us-central1/reasoningEngines/7053546862334181376`
- **Capabilities**: Runs Python code safely inside Google Cloud Agent Engine sandboxes for complex calculations, data transformations, and analysis.

### 8. 💻 ADK Web Playground UI
- **URL**: `http://localhost:8080`
- **Capabilities**: Interactive local dev UI for testing agent conversations, viewing tool call traces, and rendering image artifacts.
