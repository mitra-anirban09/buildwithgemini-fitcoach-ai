"""Gemini Omni Flash Video generation tool for FitCoach AI using ADK ToolContext and Cloud Storage."""

import base64
import uuid
import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage
import requests
from google.adk.tools import ToolContext
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-02-210a21fedfc2"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-02-210a21fedfc2"


async def generate_fitness_video(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generate a short fitness video demonstration using gemini-omni-flash-preview in the global region.

    Saves the video artifact to the Playground UI and uploads it to Cloud Storage to return its public HTTPS URL.

    Args:
        prompt: Description of the exercise technique, workout movement, or fitness activity to demonstrate (e.g. 'Proper squat form demonstration', 'Dumbbell bicep curl technique').
        tool_context: The ADK tool context used to save the generated video artifact.

    Returns:
        Public HTTPS URL of the uploaded video on Cloud Storage.
    """
    try:
        # Get GCP Auth Bearer Token
        credentials, _ = google.auth.default()
        credentials.refresh(Request())
        token = credentials.token

        url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/global/interactions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        full_prompt = (
            f"A high-quality 3-second fitness demonstration video showing: {prompt}. "
            "Smooth motion, professional fitness form."
        )

        body = {
            "model": "gemini-omni-flash-preview",
            "input": [
                {
                    "type": "text",
                    "text": full_prompt,
                }
            ],
            "response_format": [
                {
                    "type": "video",
                }
            ],
        }

        response = requests.post(url, headers=headers, json=body, timeout=120)
        if response.status_code != 200:
            return f"Interactions API returned status code {response.status_code}: {response.text[:300]}"

        data = response.json()
        video_bytes = None

        steps = data.get("steps", [])
        for step in steps:
            if step.get("type") == "model_output":
                for item in step.get("content", []):
                    if "inline_data" in item and "data" in item["inline_data"]:
                        video_bytes = base64.b64decode(item["inline_data"]["data"])
                        break
                    elif "bytes_base64_encoded" in item:
                        video_bytes = base64.b64decode(item["bytes_base64_encoded"])
                        break
                    elif "data" in item:
                        video_bytes = base64.b64decode(item["data"])
                        break
                    elif "uri" in item:
                        v_res = requests.get(item["uri"], timeout=60)
                        if v_res.status_code == 200:
                            video_bytes = v_res.content
                            break

        if not video_bytes:
            return "Failed to extract video bytes from gemini-omni-flash-preview response."

        filename = f"fitness_video_{uuid.uuid4().hex[:8]}.mp4"

        # 1. Save artifact to ToolContext for Playground UI
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload video bytes directly to GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Successfully generated fitness video!\nPublic Video URL: {public_url}"

    except Exception as e:
        return f"Error generating fitness video: {e}"
