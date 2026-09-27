import asyncio
import os
import glob
import subprocess
from playwright.async_api import async_playwright
from create_lofi_music import generate_lofi_track

async def record_demo():
    video_dir = "/config/Desktop/Session1/fitcoach-ai/demo_video"
    os.makedirs(video_dir, exist_ok=True)
    
    # 1. Synthesize upbeat lo-fi audio track first
    audio_path = "/config/Desktop/Session1/fitcoach-ai/lofi_track.wav"
    generate_lofi_track(filename=audio_path, duration=45.0)
    
    # 2. Record browser session with Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir=video_dir,
            record_video_size={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        print("Navigating to FitCoach AI frontend...")
        await page.goto("http://localhost:8085", wait_until="networkidle")
        await asyncio.sleep(2)
        
        # Step 1: First Prompt (Core App Functionality: Lower back friendly workout plan)
        prompt_1 = "Create a balanced workout plan for fat loss and muscle gain keeping in mind I have a lower back injury."
        print(f"Sending Prompt 1: {prompt_1}")
        await page.fill("#input", prompt_1)
        await asyncio.sleep(1)
        await page.click("button.send-btn")
        
        # Wait for AI reply to stream in and display
        print("Waiting for Prompt 1 response...")
        await page.wait_for_selector(".msg-wrapper.agent", timeout=30000)
        await asyncio.sleep(10)
        
        # Step 2: Second Prompt (Richer prompt demonstrating video tool call)
        prompt_2 = "Can you show me a video demonstration of proper squat technique for lower back protection?"
        print(f"Sending Prompt 2: {prompt_2}")
        await page.fill("#input", prompt_2)
        await asyncio.sleep(1)
        await page.click("button.send-btn")
        
        print("Waiting for Prompt 2 response and video tool call...")
        await asyncio.sleep(20)
        
        print("Closing browser context to finalize raw video...")
        await context.close()
        await browser.close()

    # Locate raw recorded webm video file
    videos = glob.glob(f"{video_dir}/*.webm")
    if not videos:
        print("No raw video file found in video_dir.")
        return None
        
    raw_video = videos[0]
    output_video = "/config/Desktop/Session1/fitcoach-ai/fitcoach_agent_demo.webm"
    output_mp4 = "/config/Desktop/Session1/fitcoach-ai/fitcoach_agent_demo.mp4"
    
    # 3. Use Playwright's ffmpeg to combine raw video with upbeat lo-fi background music
    ffmpeg_bin = "/config/.cache/ms-playwright/ffmpeg-1011/ffmpeg-linux"
    print("Combining video with upbeat lo-fi background music via FFmpeg...")
    
    cmd = [
        ffmpeg_bin, "-y",
        "-i", raw_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, check=True)
    print(f"Demo video with lo-fi music successfully saved to: {output_video}")
    
    # Also save as MP4 in artifact path
    artifact_mp4 = "/config/.gemini/antigravity/brain/c6f73271-1622-4d42-986e-4385bcebbb1e/fitcoach_agent_demo.webm"
    subprocess.run(["cp", output_video, artifact_mp4], check=True)
    
    return output_video

if __name__ == "__main__":
    asyncio.run(record_demo())
