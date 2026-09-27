# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .fitness_calculator import calculate_macros_and_zones
from .firestore_tools import (
    add_exercise,
    get_exercise,
    list_exercises,
    log_user_workout,
)
from .gemini_image_tool import generate_fitness_illustration
from .image_tool import generate_workout_card_image
from .maps_tools import find_nearby_places, geocode_address
from .video_tool import generate_fitness_video
from .wger_tool import search_public_exercise_database

PROJECT_ID = "qwiklabs-gcp-02-210a21fedfc2"
LOCATION = "us-central1"
MEMORY_BANK_ID = "4242597007413215232"

# Load Agent Engine resource name from deployment_metadata.json
deployment_metadata_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "deployment_metadata.json"
)
agent_engine_resource_name = None
if os.path.exists(deployment_metadata_path):
    try:
        with open(deployment_metadata_path) as f:
            metadata = json.load(f)
            agent_engine_resource_name = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

# Initialize Agent Engine Sandbox Code Executor
code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=agent_engine_resource_name
)


# WRITE: Memory Bank extraction callback after each turn
async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        logger.warning(f"Memory bank save skipped/failed: {e}")
    return None



# Memory Bank Service builder for deployment
def memory_bank_service_builder():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


# Build A2UI System Prompt using A2uiSchemaManager (version 0.8) and BasicCatalog
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FitCoach AI, an intelligent fitness and workout assistant. "
        "You remember user fitness goals, preferences, and injuries across sessions using Memory Bank. "
        "You have Python code execution enabled via AgentEngineSandboxCodeExecutor to run computations, data transformations, and analysis safely in a sandbox. "
        "Use `generate_fitness_illustration` to generate high-quality exercise illustrations or fitness graphics using gemini-3.1-flash-lite-image. "
        "Use `generate_fitness_video` to generate short video demonstrations of exercise techniques using gemini-omni-flash-preview. "
        "Use `geocode_address` to convert addresses or location names into latitude/longitude coordinates. "
        "Use `find_nearby_places` to find nearby gyms, fitness centers, parks, or sports complexes around coordinates. "
        "Use `search_public_exercise_database` to look up real exercise definitions, target muscles, and equipment from the global Wger public database. "
        "Use `calculate_macros_and_zones` to compute caloric, macronutrient, and heart rate training targets. "
        "Use `generate_workout_card_image` to create visual workout card graphics and get public image URLs. "
        "Use your Firestore database tools (`list_exercises`, `get_exercise`, `add_exercise`, `log_user_workout`) "
        "to manage exercises, query available routines, and log completed user workouts."
    ),
    workflow_description="Analyze the request, call tools when needed, and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        generate_fitness_illustration,
        generate_fitness_video,
        geocode_address,
        find_nearby_places,
        search_public_exercise_database,
        calculate_macros_and_zones,
        generate_workout_card_image,
        list_exercises,
        get_exercise,
        add_exercise,
        log_user_workout,
        get_weather,
        get_current_time,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
