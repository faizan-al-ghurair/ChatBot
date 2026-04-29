from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from enum import Enum
import anthropic
import openai
import httpx
import tempfile
import os
import json


async def download_and_transcribe(s3_url: str) -> dict:
    """Download audio file from S3 signed URL and transcribe using Whisper."""

    # download audio bytes from S3
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(s3_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download audio from S3. Status: {response.status_code}"
            )
        audio_bytes = response.content

    # extract file extension from URL path (strip query params first)
    url_path = s3_url.split("?")[0]
    suffix = os.path.splitext(url_path)[1] or ".mp4"

    # write to temp file so Whisper can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
            )
        return {
            "text": transcription.text,
            "language": transcription.language
        }
    finally:
        os.unlink(tmp_path)

# ─── routes ──────────────────────────────────────────────────────────────────
