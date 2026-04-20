from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

# ─── navigation map ───────────────────────────────────────────────────────────
# each screen has its vectors (all text from the screen) which helps
# claude understand what the screen is about in any language

NAVIGATION_MAP = {
    "lateLogin": {
        "id": 100,
        "navigation": "lateLogin",
        "navigationText": "Late Login",
        "vectors": [
            "You are late for your shift!", "Unblock your meter device",
            "Request late login", "late", "Do you have a reason for a late login?",
            "Requesting a late login without justification will result in an internal fine",
            "Report late login", "Your Late login request has been sent!",
            "It will take 10 to 15 minutes to unlock your meter.",
            "Your Late login has been accepted!", "Your Late login has been rejected!",
            "تأخر في تسجيل الدخول", "دیر سے لاگ ان", "میٹر انلاک"
        ]
    },
    "Notifications": {
        "id": 200,
        "navigation": "Notifications",
        "navigationText": "Notifications",
        "vectors": [
            "Notifications", "All the latest news in a single page",
            "messages", "message", "read", "unread", "news", "new message",
            "priority", "newest first", "unread first", "anything new",
            "إشعارات", "رسائل", "اطلاعات", "نوٹیفکیشن", "پیغام"
        ]
    },
    "myCalendar": {
        "id": 300,
        "navigation": "myCalendar",
        "navigationText": "My Calendar",
        "vectors": [
            "Calendar", "Your calendar", "my calendar", "event", "appointment",
            "schedule", "Local leave", "Annual vehicle review",
            "Request a modification", "change date",
            "تقويم", "کیلنڈر", "شيدول", "تاریخ"
        ]
    },
    "myFinances": {
        "id": 400,
        "navigation": "myFinances",
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
    "hr": {
        "id": 500,
        "navigation": "hr",
        "navigationText": "HR",
        "vectors": [
            "HR", "Everything you need related to your leaves, documents and payslips",
            "Leaves", "Documents", "Passport", "insurance", "VISA",
            "Passport collection", "Payslips", "talk to hr", "human resources",
            "الموارد البشرية", "ایچ آر", "دستاویزات", "تنخواہ"
        ]
    },
    "MyScore": {
        "id": 600,
        "navigation": "myScore",
        "navigationText": "My Score",
        "vectors": [
            "My Score", "Learn how to be a better driver", "overall score",
            "performance", "behaviour", "bonus", "challenges", "ct champions",
            "fly for free", "driver a taxi win a taxi", "driver comparison",
            "customer satisfaction", "reviews", "trends", "points", "pts",
            "درجه", "اسکور", "کارکردگی", "رویہ"
        ]
    },
    "leaves": {
        "id": 700,
        "navigation": "leaves",
        "navigationText": "Leaves",
        "vectors": [
            "Leaves", "Your leaves in a single place", "Upcoming leaves",
            "Previous leaves", "Request a new leave", "Approved", "Local leave",
            "Emergency leave", "Rejected", "annual leave", "sick leave",
            "What kind of leave you need", "Request leave", "day off",
            "إجازة", "إجازات", "چھٹی", "رخصت", "سالانہ چھٹی"
        ]
    },
    "paySlips": {
        "id": 800,
        "navigation": "paySlips",
        "navigationText": "Pay Slips",
        "vectors": [
            "Payslips", "salary slip", "pay slip", "monthly pay",
            "salary", "payment", "wages", "كشف الراتب", "قسيمة الراتب",
            "تنخواہ سلپ", "تنخواہ"
        ]
    },
    "documents": {
        "id": 900,
        "navigation": "documents",
        "navigationText": "Documents",
        "vectors": [
            "Documents", "Passport", "insurance", "VISA", "driving license",
            "documents", "files", "وثائق", "مستندات", "دستاویزات"
        ]
    },
    "createTicket": {
        "id": 1500,
        "navigation": "createTicket",
        "navigationText": "Create Ticket",
        "vectors": [
            "ticket", "support ticket", "open ticket", "new ticket",
            "Careem issue", "complaint", "help ticket", "issue",
            "تذكرة", "شكوى", "ٹکٹ", "شکایت"
        ]
    },
    "VehiclePartnerSearchList": {
        "id": 1500,
        "navigation": "VehiclePartnerSearchList",
        "navigationText": "Vehicle Partner Search",
        "vectors": [
            "search partner", "find partner", "partnership request",
            "Contact partner", "permanent vehicle", "vehicle partner",
            "شريك", "پارٹنر تلاش"
        ]
    },
    "breakDownScreen": {
        "id": 1500,
        "navigation": "breakDownScreen",
        "navigationText": "Break Down",
        "vectors": [
            "Breakdown", "On Demand Maintenance", "Did you have a breakdown",
            "A/C", "Brakes", "Engine", "Battery", "tow truck",
            "car problem", "vehicle issue", "maintenance",
            "عطل", "خرابی", "گاڑی خراب"
        ]
    },
    "behaviourBonus": {
        "id": 1500,
        "navigation": "behaviourBonus",
        "navigationText": "Behaviour Bonus",
        "vectors": [
            "behaviour bonus", "win 400", "Reach 4.3", "bonus score",
            "مكافأة السلوك", "بونس", "انعام"
        ]
    },
    "challengesList": {
        "id": 1500,
        "navigation": "challengesList",
        "navigationText": "Challenges",
        "vectors": [
            "Challenges", "CT Champions", "Fly for free",
            "Drive a Taxi Win a Taxi", "challenges list",
            "تحديات", "چیلنج"
        ]
    },
    "outStanding": {
        "id": 1500,
        "navigation": "outStanding",
        "navigationText": "Outstanding",
        "vectors": [
            "Outstanding", "Outstanding amount", "Total Outstanding",
            "Internal Fines", "RTA Fines", "Remaining Outstanding",
            "owed", "debt", "balance due",
            "المستحقات", "باقی رقم"
        ]
    },
    "accountStatement": {
        "id": 1500,
        "navigation": "accountStatement",
        "navigationText": "Account Statement",
        "vectors": [
            "Account Statement", "transactions", "Download Account Statement",
            "financial report", "statement", "كشف الحساب", "اکاؤنٹ سٹیٹمنٹ"
        ]
    },
    "fines": {
        "id": 1500,
        "navigation": "fines",
        "navigationText": "Fines",
        "vectors": [
            "Fine enquiry", "Dispute fine", "how much fine i have",
            "Your fines", "RTA fine", "Fine dispute", "traffic fine",
            "internal fine", "penalty",
            "الغرامات", "جريمة", "جرمانہ", "فائن"
        ]
    },
}

# ─── build a clean summary for claude to understand all screens ───────────────

def build_navigation_context() -> str:
    lines = []
    for key, screen in NAVIGATION_MAP.items():
        vectors_sample = ", ".join(screen["vectors"][:8])
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

You must ALWAYS respond with valid JSON only. No extra text, no explanation, just JSON.

AVAILABLE SCREENS:
{NAVIGATION_CONTEXT}

RULES:
1. If user intent matches a screen → return navigation response
2. If user asks a general question or intent is unclear → return no-navigation response
3. You support English, Arabic, and Urdu — detect and respond in the same language
4. Never make up screen names — only use screens listed above
5. Be smart about matching — "show me my money" should match myFinances, "I'm late" should match lateLogin

RESPONSE FORMAT when navigation found:
{{
  "message": "friendly message in user's language directing them to the screen",
  "navigate": true,
  "navigation": "exact navigation key from the list",
  "navigationText": "screen display name",
  "id": screen_id_number
}}

RESPONSE FORMAT when no navigation found:
{{
  "message": "helpful response in user's language",
  "navigate": false,
  "navigation": null,
  "navigationText": null,
  "id": null
}}
"""

# ─── conversation history ─────────────────────────────────────────────────────

conversation_history = []

# ─── request model ────────────────────────────────────────────────────────────

class Message(BaseModel):
    message: str

# ─── routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "Navigation bot is running!", "screens": len(NAVIGATION_MAP)}

@app.post("/chat")
def chat(body: Message):
    conversation_history.append({
        "role": "user",
        "content": body.message
    })

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )

        raw_answer = response.content[0].text.strip()
        
        # debug — print what claude actually returned
        print(f"Claude raw response: {raw_answer}")

        # strip markdown code blocks if claude added them
        if raw_answer.startswith("```"):
            raw_answer = raw_answer.split("```")[1]
            if raw_answer.startswith("json"):
                raw_answer = raw_answer[4:]
            raw_answer = raw_answer.strip()

        # parse the JSON response from claude
        try:
            parsed = json.loads(raw_answer)
        except json.JSONDecodeError:
            print(f"JSON parse failed for: {raw_answer}")
            parsed = {
                "message": "I'm sorry, I didn't understand that. Could you rephrase?",
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

    except Exception as e:
        print(f"Error: {e}")
        return {
            "message": "Something went wrong. Please try again.",
            "navigate": False,
            "navigation": None,
            "navigationText": None,
            "id": None,
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
            {"key": k, "navigation": v["navigation"], "label": v["navigationText"]}
            for k, v in NAVIGATION_MAP.items()
        ]
    }
