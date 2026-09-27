import glob
import os
import imageio
from PIL import Image

def convert_webm_to_gif(output_gif="demo.gif"):
    video_files = sorted(glob.glob("/config/Desktop/Session1/fitcoach-ai/demo_video/*.webm"), key=os.path.getmtime, reverse=True)
    if not video_files:
        print("No webm video files found!")
        return None
        
    webm_file = video_files[0]
    print(f"Reading video file: {webm_file}")
    
    reader = imageio.get_reader(webm_file)
    fps = reader.get_meta_data().get('fps', 25)
    
    # Subsample frames: take 1 frame every 6 frames (~4 fps) for fast saving & lightweight GIF size
    step = 6
    frames = []
    
    for i, frame in enumerate(reader):
        if i % step == 0:
            img = Image.fromarray(frame)
            # Resize image to width 540 for web friendliness
            w, h = img.size
            new_w = 540
            new_h = int(h * (new_w / w))
            resized_img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            # Convert to 256-color palette image
            paletted_img = resized_img.quantize(colors=128)
            frames.append(paletted_img)
            
    print(f"Extracted {len(frames)} frames. Writing looping GIF: {output_gif}...")
    
    if frames:
        frames[0].save(
            output_gif,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            duration=250, # 250ms per frame = 4 fps
            loop=0
        )
        size_mb = os.path.getsize(output_gif) / (1024 * 1024)
        print(f"SUCCESS: Looping GIF created: {output_gif} ({size_mb:.2f} MB)")
        return output_gif
    return None

if __name__ == "__main__":
    convert_webm_to_gif()
