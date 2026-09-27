"""Gemini 3.1 Flash Lite Image generation tool for FitCoach AI using ADK ToolContext and Cloud Storage."""

import uuid
from google import genai
from google.cloud import storage
from google.adk.tools import ToolContext
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-02-210a21fedfc2"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-02-210a21fedfc2"


async def generate_fitness_illustration(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generate a fitness or exercise illustration using gemini-3.1-flash-lite-image in the global region.

    Saves the image artifact to the Playground UI and uploads it to Cloud Storage to return its public URL.

    Args:
        prompt: Description of the exercise, workout routine, or nutrition item to illustrate (e.g. 'Illustrated guide for barbell squat form', 'High-protein post-workout meal graphic').
        tool_context: The ADK tool context used to save the generated image artifact.

    Returns:
        Public HTTPS URL of the uploaded image on Cloud Storage.
    """
    try:
        # Initialize GenAI Client in global region with Vertex AI
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        full_prompt = (
            f"A clean, high-quality, professional fitness illustration of: {prompt}. "
            "Modern aesthetic, clear details, high resolution."
        )

        # Call gemini-3.1-flash-lite-image in global region requesting IMAGE modality
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=[types.Modality.IMAGE],
            ),
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return "Failed to generate image bytes from gemini-3.1-flash-lite-image."

        filename = f"fitness_illustration_{uuid.uuid4().hex[:8]}.png"

        # 1. Save artifact to ToolContext for Playground UI
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload image bytes directly to GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Successfully generated fitness illustration!\nPublic Image URL: {public_url}"

    except Exception as e:
        return f"Error generating fitness illustration: {e}"
