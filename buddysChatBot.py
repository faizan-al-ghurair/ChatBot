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

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── clients ─────────────────────────────────────────────────────────────────

anthropic_client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

openai_client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# ─── navigation enum ─────────────────────────────────────────────────────────

class Nav(str, Enum):
    def __str__(self):
        return self.value

    LATE_LOGIN                  = "lateLogin"
    NOTIFICATIONS               = "Notifications"
    MY_CALENDAR                 = "myCalendar"
    MY_FINANCES                 = "myFinances"
    HR                          = "hr"
    MY_SCORE                    = "myScore"
    LEAVES                      = "leaves"
    PAY_SLIPS                   = "paySlips"
    DOCUMENTS                   = "documents"
    CREATE_TICKET               = "createTicket"
    VEHICLE_PARTNER_SEARCH      = "VehiclePartnerSearchList"
    BREAK_DOWN                  = "breakDownScreen"
    BEHAVIOUR_BONUS             = "behaviourBonus"
    CHALLENGES_LIST             = "challengesList"
    OUTSTANDING                 = "outStanding"
    ACCOUNT_STATEMENT           = "accountStatement"
    FINES                       = "fines"
    PROFILE_PHOTO               = "profilePhoto"

# ─── navigation map ───────────────────────────────────────────────────────────

NAVIGATION_MAP = {
    Nav.LATE_LOGIN: {
        "id": 100,
        "navigation": Nav.LATE_LOGIN,
        "navigationText": "Late Login",
        "vectors": [
            "You are late for your shift!", "Unblock your meter device",
            "Request late login", "late login", "Do you have a reason for a late login?",
            "Requesting a late login without justification will result in an internal fine",
            "Report late login", "Your Late login request has been sent!",
            "It will take 10 to 15 minutes to unlock your meter.",
            "Your Late login has been accepted!", "Your Late login has been rejected!",
            "تأخر في تسجيل الدخول", "دیر سے لاگ ان", "میٹر انلاک", "late"
        ]
    },
    Nav.NOTIFICATIONS: {
        "id": 200,
        "navigation": Nav.NOTIFICATIONS,
        "navigationText": "Notifications",
        "vectors": [
            "Notifications", "All the latest news in a single page",
            "messages", "message", "read", "unread", "news", "new message",
            "priority", "newest first", "unread first", "anything new",
            "إشعارات", "رسائل", "اطلاعات", "نوٹیفکیشن", "پیغام"
        ]
    },
    Nav.MY_CALENDAR: {
        "id": 300,
        "navigation": Nav.MY_CALENDAR,
        "navigationText": "My Calendar",
        "vectors": [
            "Calendar", "Your calendar", "my calendar", "event", "appointment",
            "schedule", "Local leave", "Annual vehicle review",
            "Request a modification", "change date",
            "تقويم", "کیلنڈر", "شيدول", "تاریخ"
        ]
    },
    Nav.MY_FINANCES: {
        "id": 400,
        "navigation": Nav.MY_FINANCES,
        "navigationText": "My Finances",
        "vectors": [
            "collections", "Finances", "Daily avg", "Commission", "Outstanding",
            "Account Statement", "Fine enquiry", "My Collections", "Total collections",
            "Days collections", "Daily collections", "Days worked", "Surcharges",
            "Shift collections details", "Day shift", "Night shift",
            "Collections forecast", "forecast", "earnings", "money", "income",
            "ماليتي", "مالیات", "کمائی", "پیسے", "آمدنی"
        ]
    },
    Nav.HR: {
        "id": 500,
        "navigation": Nav.HR,
        "navigationText": "HR",
        "vectors": [
            "HR", "Everything you need related to your leaves, documents and payslips",
            "Leaves","sick leave","emergancy leave", "Documents", "Passport", "insurance", "VISA",
            "Passport collection", "Payslips", "talk to hr", "human resources",
            "الموارد البشرية", "ایچ آر", "دستاویزات", "تنخواہ"
        ]
    },
    Nav.MY_SCORE: {
        "id": 600,
        "navigation": Nav.MY_SCORE,
        "navigationText": "My Score",
        "vectors": [
            "My Score", "Learn how to be a better driver", "overall score",
            "performance", "behaviour", "bonus", "challenges", "ct champions",
            "fly for free", "driver a taxi win a taxi", "driver comparison",
            "customer satisfaction", "reviews", "trends", "points", "pts",
            "درجه", "اسکور", "کارکردگی", "رویہ"
        ]
    },
    Nav.LEAVES: {
        "id": 700,
        "navigation": Nav.LEAVES,
        "navigationText": "Leaves",
        "vectors": [
            "Leaves", "Your leaves in a single place", "Upcoming leaves",
            "Previous leaves", "Request a new leave", "Approved", "Local leave",
            "Emergency leave", "Rejected", "annual leave", "sick leave",
            "What kind of leave you need", "Request leave", "day off",
            "إجازة", "إجازات", "چھٹی", "رخصت", "سالانہ چھٹی"
        ]
    },
    Nav.PAY_SLIPS: {
        "id": 800,
        "navigation": Nav.PAY_SLIPS,
        "navigationText": "Pay Slips",
        "vectors": [
            "Payslips", "salary slip", "pay slip", "monthly pay",
            "salary", "payment", "wages", "كشف الراتب", "قسيمة الراتب",
            "تنخواہ سلپ", "تنخواہ"
        ]
    },
    Nav.DOCUMENTS: {
        "id": 900,
        "navigation": Nav.DOCUMENTS,
        "navigationText": "Documents",
        "vectors": [
            "Documents", "Passport", "insurance", "VISA", "driving license",
            "documents", "files", "وثائق", "مستندات", "دستاویزات"
        ]
    },
    Nav.CREATE_TICKET: {
        "id": 1000,
        "navigation": Nav.CREATE_TICKET,
        "navigationText": "Create Ticket",
        "vectors": [
            "ticket", "support ticket", "open ticket", "new ticket",
            "Careem issue", "complaint", "help ticket", "issue",
            "تذكرة", "شكوى", "ٹکٹ", "شکایت"
        ]
    },
    Nav.VEHICLE_PARTNER_SEARCH: {
        "id": 1100,
        "navigation": Nav.VEHICLE_PARTNER_SEARCH,
        "navigationText": "Vehicle Partner Search",
        "vectors": [
            "search partner", "find partner", "partnership request",
            "Contact partner", "permanent vehicle", "vehicle partner",
            "شريك", "پارٹنر تلاش"
        ]
    },
    Nav.BREAK_DOWN: {
        "id": 1200,
        "navigation": Nav.BREAK_DOWN,
        "navigationText": "Break Down",
        "vectors": [
            "Breakdown", "On Demand Maintenance", "Did you have a breakdown",
            "A/C", "Brakes", "Engine", "Battery", "tow truck",
            "car problem", "vehicle issue", "maintenance",
            "عطل", "خرابی", "گاڑی خراب"
        ]
    },
    Nav.BEHAVIOUR_BONUS: {
        "id": 1300,
        "navigation": Nav.BEHAVIOUR_BONUS,
        "navigationText": "Behaviour Bonus",
        "vectors": [
            "behaviour bonus", "win 400", "Reach 4.3", "bonus score",
            "مكافأة السلوك", "بونس", "انعام"
        ]
    },
    Nav.CHALLENGES_LIST: {
        "id": 1400,
        "navigation": Nav.CHALLENGES_LIST,
        "navigationText": "Challenges",
        "vectors": [
            "Challenges", "CT Champions", "Fly for free",
            "Drive a Taxi Win a Taxi", "challenges list",
            "تحديات", "چیلنج"
        ]
    },
    Nav.OUTSTANDING: {
        "id": 1500,
        "navigation": Nav.OUTSTANDING,
        "navigationText": "Outstanding",
        "vectors": [
            "Outstanding", "Outstanding amount", "Total Outstanding",
            "Internal Fines", "RTA Fines", "Remaining Outstanding",
            "owed", "debt", "balance due",
            "المستحقات", "باقی رقم"
        ]
    },
    Nav.ACCOUNT_STATEMENT: {
        "id": 1600,
        "navigation": Nav.ACCOUNT_STATEMENT,
        "navigationText": "Account Statement",
        "vectors": [
            "Account Statement", "transactions", "Download Account Statement",
            "financial report", "statement", "كشف الحساب", "اکاؤنٹ سٹیٹمنٹ"
        ]
    },
    Nav.FINES: {
        "id": 1700,
        "navigation": Nav.FINES,
        "navigationText": "Fines",
        "vectors": [
            "Fine enquiry", "Dispute fine", "how much fine i have",
            "Your fines", "RTA fine", "Fine dispute", "traffic fine",
            "internal fine", "penalty",
            "الغرامات", "جريمة", "جرمانہ", "فائن"
        ]
    },
    Nav.PROFILE_PHOTO: {
        "id": 1800,
        "navigation": Nav.PROFILE_PHOTO,
        "navigationText": "Profile Photo",
        "vectors": [
            "profile photo", "upload photo", "change photo", "update photo",
            "profile picture", "profile image", "change profile", "my photo",
            "تصویر", "پروفائل تصویر", "صورة الملف الشخصي", "تغيير الصورة"
        ]
    },
}

# ─── build navigation context for claude ─────────────────────────────────────

def build_navigation_context() -> str:
    lines = []
    for key, screen in NAVIGATION_MAP.items():
        vectors_sample = ", ".join(screen["vectors"][:10])
        lines.append(
            f'- Screen: "{screen["navigation"]}" | '
            f'Label: "{screen["navigationText"]}" | '
            f'Keywords: {vectors_sample}'
        )
    return "\n".join(lines)

NAVIGATION_CONTEXT = build_navigation_context()

# ─── system prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are a smart navigation assistant for a taxi driver mobile app.
Your ONLY job is to understand what screen the user wants to go to and return a JSON response.

You must ALWAYS respond with raw valid JSON only.
No markdown, no backticks, no explanation. Just the JSON object.

AVAILABLE SCREENS:
{NAVIGATION_CONTEXT}

RULES:
1. If user intent matches a screen → return navigation response
2. If user asks a general question or intent is unclear → return no-navigation response
3. CRITICAL — Language rule: Identify the language of the user's message. The "message" field in your JSON response MUST be written in that EXACT same language. If the user writes in French, respond in French. If Turkish, respond in Turkish. If Urdu, respond in Urdu. NEVER respond in English unless the user wrote in English.
4. Never make up screen names — only use screens listed above
5. Be smart — "show me my money" → myFinances, "I am late" → lateLogin, "مجھے چھٹی چاہیے" → leaves

RESPONSE FORMAT when navigation found:
{{
  "message": "friendly short message written in the SAME language as the user's input",
  "navigate": true,
  "navigation": "exact navigation key from the list",
  "navigationText": "screen display name",
  "id": screen_id_number
}}

RESPONSE FORMAT when no navigation found:
{{
  "message": "helpful response written in the SAME language as the user's input",
  "navigate": false,
  "navigation": null,
  "navigationText": null,
  "id": null
}}

IMPORTANT: Return raw JSON only. No markdown. No backticks. No explanation. Just the JSON object.
"""

# ─── conversation history ─────────────────────────────────────────────────────

conversation_history = []

# ─── request model ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    type: str                        # "text" or "audio"
    message: Optional[str] = None   # filled when type = "text"
    url: Optional[str] = None       # filled when type = "audio" — S3 signed URL

# ─── helpers ─────────────────────────────────────────────────────────────────

def process_with_claude(text: str) -> dict:
    """Run text through Claude navigation logic and return parsed response."""
    conversation_history.append({
        "role": "user",
        "content": text
    })

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    raw_answer = response.content[0].text.strip()
    print(f"Claude raw response: {raw_answer}")

    # strip markdown code blocks if claude wrapped the response
    if raw_answer.startswith("```"):
        raw_answer = raw_answer.split("```")[1]
        if raw_answer.startswith("json"):
            raw_answer = raw_answer[4:]
        raw_answer = raw_answer.strip()

    try:
        parsed = json.loads(raw_answer)
    except json.JSONDecodeError:
        print(f"JSON parse failed: {raw_answer}")
        parsed = {
            "message": "I could not understand that. Please try again.",
            "navigate": False,
            "navigation": None,
            "navigationText": None,
            "id": None
        }

    conversation_history.append({
        "role": "assistant",
        "content": raw_answer
    })

    return parsed


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

@app.get("/")
def root():
    return {
        "status": "Navigation bot is running",
        "screens": len(NAVIGATION_MAP),
        "supported_types": ["text", "audio"]
    }


@app.post("/chat")
async def chat(body: ChatRequest):
    """
    Unified endpoint — handles both text and audio input.

    Text example:
    POST /chat
    { "type": "text", "message": "I need a leave", "url": null }

    Audio example:
    POST /chat
    { "type": "audio", "message": null, "url": "https://buddyapp-dev-bucket.s3.amazonaws.com/..." }

    Response (both types return same shape):
    {
        "message": "Here are your leaves",
        "navigate": true,
        "navigation": "leaves",
        "navigationText": "Leaves",
        "id": 700,
        "input_type": "audio",
        "transcribed_text": "I need a leave",   <- null for text input
        "language_detected": "en"               <- null for text input
    }
    """
    try:

        # ── text input ────────────────────────────────────────────────────────
        if body.type == "text":
            if not body.message or not body.message.strip():
                raise HTTPException(
                    status_code=400,
                    detail="message field is required when type is text"
                )

            result = process_with_claude(body.message.strip())

            return {
                **result,
                "input_type": "text",
                "transcribed_text": None,
                "language_detected": None,
                "question": body.message.strip()
            }

        # ── audio input ───────────────────────────────────────────────────────
        elif body.type == "audio":
            if not body.url or not body.url.strip():
                raise HTTPException(
                    status_code=400,
                    detail="url field is required when type is audio"
                )

            # step 1 — download from S3 and transcribe with Whisper
            print(f"Downloading audio from S3...")
            transcription = await download_and_transcribe(body.url)
            transcribed_text = transcription["text"]
            language_detected = transcription["language"]
            print(f"Transcribed [{language_detected}]: {transcribed_text}")

            # step 2 — process transcribed text through Claude
            result = process_with_claude(transcribed_text)

            return {
                **result,
                "input_type": "audio",
                "transcribed_text": transcribed_text,
                "language_detected": language_detected,
                "question": transcribed_text
            }

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type '{body.type}'. Accepted values: 'text' or 'audio'"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "message": "Something went wrong. Please try again.",
            "navigate": False,
            "navigation": None,
            "navigationText": None,
            "id": None,
            "input_type": body.type,
            "transcribed_text": None,
            "language_detected": None,
            "error": str(e)
        }


@app.get("/history")
def get_history():
    return {"history": conversation_history}


@app.delete("/clear")
def clear_history():
    conversation_history.clear()
    return {"status": "History cleared!"}


@app.get("/screens")
def get_screens():
    return {
        "total": len(NAVIGATION_MAP),
        "screens": [
            {
                "key": k,
                "navigation": v["navigation"],
                "label": v["navigationText"],
                "id": v["id"]
            }
            for k, v in NAVIGATION_MAP.items()
        ]
    }