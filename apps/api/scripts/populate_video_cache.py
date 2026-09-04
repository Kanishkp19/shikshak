#!/usr/bin/env python3
"""
Shikshak AI — Populate Video Cache CLI.

Registers manually downloaded Google Flow clips into Supabase Storage and
the `video_cache` table. One-time human-run command.
No browser automation or web scraping.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import uuid

# Ensure apps/api is in sys.path when script is executed directly
current_dir = Path(__file__).resolve().parent
api_root = current_dir.parent
if str(api_root) not in sys.path:
    sys.path.insert(0, str(api_root))

from skills.caching import hash_prompt

try:
    from supabase import create_client
except ImportError:
    create_client = None


def get_supabase_client():
    if create_client is None:
        sys.exit("Error: 'supabase' Python package is required. Run: pip install supabase")

    supabase_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        sys.exit(
            "Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables must be set."
        )

    return create_client(supabase_url, service_role_key)


def populate_video_cache(
    file_path: str | Path,
    concept: str,
    visual_type: str,
    depth: str,
    language: str = "en",
    client=None,
) -> dict:
    local_path = Path(file_path).resolve()
    if not local_path.exists() or not local_path.is_file():
        sys.exit(f"Error: Specified video file does not exist: {local_path}")

    if local_path.stat().st_size == 0:
        sys.exit(f"Error: Specified video file is empty: {local_path}")

    prompt_hash = hash_prompt(
        concept=concept,
        visual_type=visual_type,
        depth=depth,
        language=language,
    )

    file_extension = local_path.suffix or ".mp4"
    storage_path = f"flow_cache/{prompt_hash}{file_extension}"

    supabase = client or get_supabase_client()

    # Upload local file to Supabase Storage bucket 'videos' with upsert
    with open(local_path, "rb") as f:
        file_bytes = f.read()

    supabase.storage.from_("videos").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"upsert": "true", "content-type": "video/mp4"},
    )

    # Upsert row into video_cache table
    record_id = str(uuid.uuid4())
    row_data = {
        "id": record_id,
        "prompt_hash": prompt_hash,
        "provider": "flow_cache",
        "storage_path": storage_path,
    }

    supabase.table("video_cache").upsert(
        row_data,
        on_conflict="prompt_hash",
    ).execute()

    return {
        "concept": concept,
        "visual_type": visual_type,
        "depth": depth,
        "language": language,
        "prompt_hash": prompt_hash,
        "storage_path": storage_path,
        "status": "success",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Register a pre-generated Google Flow clip into the Shikshak AI video cache."
    )
    parser.add_argument(
        "--file",
        required=True,
        type=str,
        help="Path to the local .mp4 video clip.",
    )
    parser.add_argument(
        "--concept",
        required=True,
        type=str,
        help="The educational concept covered in the clip (e.g. 'Photosynthesis').",
    )
    parser.add_argument(
        "--visual-type",
        required=True,
        choices=["diagram", "equation", "code", "animation", "none"],
        help="Visual style of the clip.",
    )
    parser.add_argument(
        "--depth",
        required=True,
        choices=["beginner", "intermediate", "advanced"],
        help="Learning depth level.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Language code (default: 'en').",
    )

    args = parser.parse_args()

    result = populate_video_cache(
        file_path=args.file,
        concept=args.concept,
        visual_type=args.visual_type,
        depth=args.depth,
        language=args.language,
    )

    print("\n" + "=" * 60)
    print(" Flow Cache Video Clip Successfully Registered")
    print("=" * 60)
    print(f" Concept      : {result['concept']}")
    print(f" Visual Type  : {result['visual_type']}")
    print(f" Depth        : {result['depth']}")
    print(f" Language     : {result['language']}")
    print(f" Prompt Hash  : {result['prompt_hash']}")
    print(f" Storage Path : {result['storage_path']}")
    print(" Status       : SUCCESS")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
