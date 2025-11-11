#!/usr/bin/env python3
"""
Generate 3D model from bike image using Meshy.ai API

Usage:
    python scripts/generate_3d_model.py docs/bike-test.jpg

Features:
- Uploads image to Meshy.ai
- Creates image-to-3D generation task
- Polls status with progress updates
- Downloads GLB model to frontend/static/models/
- Tracks API usage and costs

Cost: ~$0.50 per generation (1 Meshy credit)
"""

import httpx
import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

# Configuration
MESHY_API_KEY = os.getenv("MESHY_API_KEY")
MESHY_BASE_URL = "https://api.meshy.ai/v2/image-to-3d"

if not MESHY_API_KEY:
    print("❌ Error: MESHY_API_KEY not found in environment")
    print("Add to .env file or export MESHY_API_KEY=msy_your_key")
    sys.exit(1)


async def upload_image_to_meshy(image_path: str) -> str:
    """
    Upload image to Meshy.ai and get public URL

    Returns:
        Public URL of uploaded image
    """
    print(f"📤 Uploading image: {image_path}")

    # Read image file
    image_data = Path(image_path).read_bytes()

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Request upload URL
        response = await client.post(
            "https://api.meshy.ai/v2/image-to-3d/upload",
            headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
            json={"filename": Path(image_path).name}
        )
        response.raise_for_status()
        upload_data = response.json()

        # Upload to presigned URL
        upload_response = await client.put(
            upload_data["url"],
            content=image_data,
            headers={"Content-Type": "image/jpeg"}
        )
        upload_response.raise_for_status()

        print(f"✅ Image uploaded successfully")
        return upload_data["url"].split('?')[0]  # Remove query params


async def create_3d_task(image_url: str) -> str:
    """
    Create image-to-3D generation task

    Args:
        image_url: Public URL of uploaded image

    Returns:
        Task ID for polling
    """
    print(f"🎨 Creating 3D generation task...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            MESHY_BASE_URL,
            headers={
                "Authorization": f"Bearer {MESHY_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "image_url": image_url,
                "enable_pbr": True,  # Physically Based Rendering textures
                "ai_model": "meshy-4",  # Latest model (best quality)
                "topology": "quad",  # Quad topology (better for animation)
                "target_polycount": 30000  # 30k polys (good for web)
            }
        )
        response.raise_for_status()
        data = response.json()

        task_id = data["id"]
        print(f"✅ Task created: {task_id}")
        print(f"⏳ Estimated time: 5-15 minutes")

        return task_id


async def poll_status(task_id: str) -> dict:
    """
    Poll task status until complete

    Args:
        task_id: Task ID from create_3d_task

    Returns:
        Final task data with model URLs
    """
    print(f"⏳ Polling status (updates every 10 seconds)...")
    print(f"⏳ This will take 5-15 minutes. Grab a coffee! ☕")

    start_time = datetime.now()
    last_progress = -1

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            response = await client.get(
                f"{MESHY_BASE_URL}/{task_id}",
                headers={"Authorization": f"Bearer {MESHY_API_KEY}"}
            )
            response.raise_for_status()
            data = response.json()

            status = data["status"]
            progress = data.get("progress", 0)

            # Only print if progress changed
            if progress != last_progress:
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"📊 Status: {status} | Progress: {progress}% | Elapsed: {elapsed:.0f}s")
                last_progress = progress

            if status == "SUCCEEDED":
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"✅ Generation complete! Total time: {elapsed:.0f}s ({elapsed/60:.1f} min)")
                return data

            elif status == "FAILED":
                error_msg = data.get("error", "Unknown error")
                raise Exception(f"❌ Generation failed: {error_msg}")

            elif status in ["PENDING", "IN_PROGRESS"]:
                await asyncio.sleep(10)  # Poll every 10 seconds

            else:
                print(f"⚠️  Unknown status: {status}")
                await asyncio.sleep(10)


async def download_model(model_url: str, output_path: str):
    """
    Download GLB file from Meshy.ai

    Args:
        model_url: URL of generated GLB model
        output_path: Local path to save model
    """
    print(f"⬇️  Downloading model to {output_path}...")

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(model_url)
        response.raise_for_status()

        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Write model file
        Path(output_path).write_bytes(response.content)

        file_size_mb = len(response.content) / (1024 * 1024)
        print(f"✅ Model downloaded: {file_size_mb:.2f} MB")


async def save_metadata(task_id: str, task_data: dict, output_path: str):
    """Save generation metadata for reference"""
    metadata = {
        "task_id": task_id,
        "generated_at": datetime.now().isoformat(),
        "model_path": output_path,
        "status": task_data["status"],
        "model_urls": task_data.get("model_urls", {}),
        "thumbnail_url": task_data.get("thumbnail_url"),
        "cost_estimate": "$0.50 (1 Meshy credit)"
    }

    metadata_path = output_path.replace(".glb", ".json")
    Path(metadata_path).write_text(json.dumps(metadata, indent=2))
    print(f"📄 Metadata saved: {metadata_path}")


async def main(image_path: str):
    """Main generation workflow"""
    print(f"\n🚀 ShredBX 3D Model Generator")
    print(f"{'='*50}")
    print(f"Input: {image_path}")
    print(f"{'='*50}\n")

    try:
        # Step 1: Upload image
        image_url = await upload_image_to_meshy(image_path)

        # Step 2: Create task
        task_id = await create_3d_task(image_url)

        # Step 3: Poll until complete
        result = await poll_status(task_id)

        # Step 4: Download model
        output_path = f"apps/frontend/static/models/bike-{task_id}.glb"
        model_url = result["model_urls"]["glb"]
        await download_model(model_url, output_path)

        # Step 5: Save metadata
        await save_metadata(task_id, result, output_path)

        # Success!
        print(f"\n{'='*50}")
        print(f"✅ SUCCESS!")
        print(f"{'='*50}")
        print(f"Model: {output_path}")
        print(f"Task ID: {task_id}")
        print(f"Thumbnail: {result.get('thumbnail_url')}")
        print(f"💰 Cost: ~$0.50 (1 Meshy credit)")
        print(f"\n📝 Next steps:")
        print(f"1. Update apps/frontend/src/routes/+page.svelte")
        print(f"2. Change model path to: /models/bike-{task_id}.glb")
        print(f"3. Run: cd apps/frontend && npm run dev")
        print(f"4. View at: http://localhost:5483")

    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_3d_model.py <image_path>")
        print("Example: python scripts/generate_3d_model.py docs/bike-test.jpg")
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"❌ Error: Image not found: {image_path}")
        sys.exit(1)

    # Run async main
    asyncio.run(main(image_path))
