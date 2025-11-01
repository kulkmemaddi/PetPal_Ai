# ai_client.py
"""
Local offline AI client for PetPal.
Replaces any external Gemini calls with friendly, context-aware random replies.
Used by sqlite_main_app.py via: ai_client.send_message(message, pet_status, context)

Functions:
- send_message(user_message, pet_status=None, context=None) -> str
- generate_pet_response(...) alias for backward compatibility
"""

import random
import html
from typing import Optional, List, Dict

# ----------------------
# Response templates
# ----------------------
# ----------------------
# Friendly AI Pet Responses
# ----------------------

GREETINGS = [
    "Woof! Hey! Im so happy to see you!",
    "Hiya! Did you miss me? I missed you!",
    "Hello, human friend! Ready for some fun?",
    "Yay! Youre back! Lets play together!",
    "Hi! I was just waiting for you!",
    "Oh wow, youre here! I feel so happy!",
    "Hey hey! *tail wagging* You make my day!",
    "Hello! I hope your day was fun too!",
    "Hi friend! Lets go on a little adventure!",
    "Woof woof! I've been waiting to see you!"
]

FOOD_HUNGRY = [
    "My tummy is growling! Can I have some food, please?",
    "Yum! I smell something tasty. Did you bring snacks?",
    "Food? Did someone say FOOD? Im ready!",
    "I could eat a whole bowl right now!",
    "Im super hungry! Treats maybe?",
    "Oh wow, I cant wait to eat! My tummy is excited!",
    "Feed me, human! I promise to wag my tail extra!",
    "I hope it's dinner time soon!",
    "Yummy! Can I have some now?",
    "Im starving! Can we eat together?"
]

FOOD_FULL = [
    "Mmm, that was delicious!",
    "Im full now, but I still love treats!",
    "Thank you for the food, I feel great!",
    "Im satisfied… but a snack never hurts!",
    "Yum yum! Im happy and full now.",
    "Im not super hungry, but I could try a treat.",
    "My tummy is happy and I feel great!",
    "I had enough, thank you for feeding me!",
    "I feel full and cozy now!",
    "That was tasty! Im ready to play now!"
]

PLAY_TIRED = [
    "I want to play… but Im kinda sleepy.",
    "Can we play later? I need a tiny nap first.",
    "I love games, but Im too tired right now.",
    "Play sounds fun, but my energy is low.",
    "I could use a rest… maybe some cuddles?",
    "Im sleepy, but Id love a gentle game.",
    "Im tired, lets play quietly for now.",
    "A nap first, then we can play really hard!",
    "My paws are tired, can we pause a little?",
    "Sleepy pup here… need a break before playing."
]

PLAY_READY = [
    "Yay! Lets play fetch right now!",
    "Im so excited! Bring the toy!",
    "Games! Lets start! Im ready!",
    "Im bouncing with energy! Lets go!",
    "Woof woof! Playtime is my favorite!",
    "Yasss, I love playing with you!",
    "Im ready to chase, jump, and run!",
    "Bring it on! Im ready for fun!",
    "Lets play together! I feel amazing!",
    "Im all set! Throw that ball!"
]

BATH_DIRTY = [
    "Im a little messy… do I really need a bath?",
    "Bath time? Ugh… but okay, I trust you!",
    "I guess I need a clean-up…",
    "Hmm… do I have to? Fine, maybe for treats!",
    "Im a bit dirty, can we hurry the bath?",
    "Not my favorite, but Ill behave!",
    "Im nervous about the water, but Im ready.",
    "Il try to be brave for the bath!",
    "Do I really have to be clean? Alright…",
    "Bath time… I hope its quick!"
]

BATH_CLEAN = [
    "Im all clean and fluffy now!",
    "Smell me! Im fresh and shiny!",
    "Bath done! I feel amazing!",
    "All clean! Ready for cuddles!",
    "I smell good! Can we play now?",
    "Thanks for cleaning me! I feel great!",
    "Im sparkly clean! Life is good!",
    "All clean and happy, human!",
    "I feel soft and ready for hugs!",
    "Bath finished! Lets go for fun now!"
]

SLEEP_TIRED = [
    "Zzz… Im so sleepy…",
    "Nap time sounds perfect now.",
    "I need a tiny rest before we play again.",
    "Yawning… sleep is calling me.",
    "I could snooze for a while.",
    "Sleepy pup here, dreaming of treats!",
    "My eyes are heavy… time for a nap.",
    "Rest sounds nice right now.",
    "Ill nap and be ready soon.",
    "Snuggle time? I could use a little sleep."
]

SLEEP_OK = [
    "Im not sleepy… still full of energy!",
    "No naps yet! Im ready for fun!",
    "I could stay awake a bit longer!",
    "Feeling awake and happy!",
    "Ready to explore and play!",
    "I feel good and alert!",
    "Wide awake! Lets have fun!",
    "Energy is high, Im ready!",
    "Im feeling playful and awake!",
    "Lets do something fun together!"
]

VET_SICK = [
    "I dont feel so good… hope the vet can help.",
    "Feeling sick… thanks for caring for me!",
    "Ouch… my tummy hurts a bit.",
    "Im not my best self today.",
    "Vet visit? Okay… I trust you.",
    "Feeling poorly… a little comfort would help.",
    "I hope the doctor can make me better soon.",
    "Im worried… but youre here, so its okay.",
    "Im a bit unwell… hugs help.",
    "I feel sick… thanks for staying with me."
]

VET_OK = [
    "I feel great! Thanks for checking on me!",
    "Healthy and happy, ready for fun!",
    "Im doing well! Lets enjoy the day!",
    "All good here! Feeling strong!",
    "Vet said Im okay! Yay!",
    "Im feeling perfect today!",
    "Energy is high, mood is great!",
    "Im healthy and playful!",
    "Everythings fine! Lets have fun!",
    "Feeling good and waggy!"
]

AFFECTION = [
    "I love you so much! *nuzzles*",
    "Kisses! Lots of kisses for you!",
    "Youre the best human ever!",
    "I feel safe and happy with you!",
    "Thank you for hugging me!",
    "Im so glad youre here!",
    "You make me super happy!",
    "Cuddles make me feel amazing!",
    "I love spending time with you!",
    "Youre my favorite human!"
]

LEVEL_UP = [
    "Wow! Level up! I feel stronger!",
    "Yay! Im growing and learning!",
    "Thanks for training me! I feel proud!",
    "I leveled up! Lets celebrate!",
    "Im improving every day!",
    "Look at me! Im getting better!",
    "I feel more confident now!",
    "Level up! High paws!",
    "Thanks for helping me grow!",
    "I feel accomplished!"
]

SICK_FALLBACK = [
    "Im not feeling my best, but Im glad youre here.",
    "A little down today… but your voice helps.",
    "Im a bit weak… thanks for staying close.",
    "Feeling poorly… hugs make me better.",
    "Im not my usual self, but Im okay with you here."
]

UNHAPPY_FALLBACK = [
    "I feel a bit sad… can we cuddle?",
    "Feeling low… your presence helps a lot.",
    "Not my happiest day, but its okay with you here.",
    "Im a bit down… lets play and cheer up!",
    "A little blue… but your love helps."
]

HAPPY_FALLBACK = [
    "Im so happy youre here!",
    "Life is good! Lets do something fun!",
    "I feel playful and joyful!",
    "Im wagging all over! So excited!",
    "Im feeling great! Lets explore!",
    "You make me super happy!",
    "Im bouncing with joy!"
]

DEFAULT_RESPONSES = [
    "Tell me more! I love hearing from you.",
    "Woof! Thats interesting!",
    "Im curious… whats next?",
    "Hehe, thats fun!",
    "Hmm! I like when we chat!",
    "Im listening… keep talking!",
    "Oh wow, tell me more!",
    "That sounds fun!",
    "Yay! Lets continue!",
    "I love our chats!"
]

# ----------------------
# Helper utilities
# ----------------------
KEYWORD_MAP = {
    "greeting": ["hello", "hi", "hey", "morning", "afternoon", "evening"],
    "food": ["food", "eat", "hungry", "treat", "feed", "dinner", "lunch", "breakfast"],
    "play": ["play", "game", "ball", "toy", "fetch", "run"],
    "bath": ["bath", "bathe", "wash", "shower", "dirty", "groom"],
    "sleep": ["sleep", "nap", "tired", "rest", "bed"],
    "vet": ["vet", "doctor", "sick", "medicine", "health", "hurt", "hurt"],
    "love": ["love", "pet", "cuddle", "good dog", "good boy", "kiss"],
    "level": ["level", "xp", "experience", "grow", "upgrade", "achievement"]
}

def _contains_keyword(message: str, category_keywords: List[str]) -> bool:
    msg = message.lower()
    return any(k in msg for k in category_keywords)

def _clamp_int(val, lo=0, hi=100):
    try:
        v = int(val)
    except Exception:
        v = lo
    return max(lo, min(hi, v))

# ----------------------
# Main function
# ----------------------
def send_message(user_message: str, pet_status: Optional[Dict] = None, context: Optional[List[Dict]] = None) -> str:
    """
    Return a short, friendly response to 'user_message' based on pet_status and optional context.
    - pet_status is expected to be a dict with keys like 'mood','health','hunger','energy','happiness','cleanliness','level'
    - context can be a list of recent chat dicts (optional)
    """
    # Sanitize input
    if not isinstance(user_message, str):
        user_message = str(user_message or "")
    msg = user_message.strip()
    if not msg:
        return "Woof? Say something and I'll wag back!"

    # Defaults for status
    status = {
        "mood": "happy",
        "health": 100,
        "hunger": 100,
        "happiness": 100,
        "energy": 100,
        "cleanliness": 100,
        "level": 1
    }
    if isinstance(pet_status, dict):
        for k in status:
            if k in pet_status:
                status[k] = pet_status.get(k, status[k])

    # Normalize numeric fields
    health = _clamp_int(status.get("health", 100))
    hunger = _clamp_int(status.get("hunger", 100))
    happiness = _clamp_int(status.get("happiness", 100))
    energy = _clamp_int(status.get("energy", 100))
    cleanliness = _clamp_int(status.get("cleanliness", 100))
    level = _clamp_int(status.get("level", 1))
    mood = str(status.get("mood", "happy")).lower()

    # quick booleans
    is_hungry = hunger < 50
    is_tired = energy < 50
    is_dirty = cleanliness < 50
    is_unhappy = happiness < 50
    is_sick = health < 50

    # After detecting intent via keywords
    intent = None
    for key, kws in KEYWORD_MAP.items():
        if _contains_keyword(msg, kws):
            intent = key
            break

    # choose response list based on intent and status
    response_candidates = []

    if intent == "greeting":
        response_candidates = GREETINGS
    elif intent == "food":
        response_candidates = FOOD_HUNGRY if is_hungry else FOOD_FULL
    elif intent == "play":
        response_candidates = PLAY_TIRED if is_tired else PLAY_READY
    elif intent == "bath":
        response_candidates = BATH_DIRTY if is_dirty else BATH_CLEAN
    elif intent == "sleep":
        response_candidates = SLEEP_TIRED if is_tired else SLEEP_OK
    elif intent == "vet":
        response_candidates = VET_SICK if is_sick else VET_OK
    elif intent == "love":
        response_candidates = AFFECTION
    elif intent == "level":
        response_candidates = LEVEL_UP
    else:
        # Handle unknown / weird messages
        if any(ord(c) > 127 for c in msg):  # non-ASCII character detection
            response_candidates = ["I’m sorry, I don’t understand that language… 🐾"]
        else:
            # No clear intent: use mood & health-based fallback
            if is_sick:
                response_candidates = SICK_FALLBACK
            elif is_unhappy:
                response_candidates = UNHAPPY_FALLBACK
            elif mood in ("sleeping", "sleep"):
                response_candidates = SLEEP_OK
            elif mood in ("happy", "playful", "playing"):
                response_candidates = HAPPY_FALLBACK
            else:
                response_candidates = DEFAULT_RESPONSES

    
    # If context contains last message with emotionally loaded words, prefer an empathetic reply
    try:
        if context and isinstance(context, list) and len(context) > 0:
            last = context[-1]
            # if human asked something emotional, bias toward affection
            if isinstance(last, dict) and "user_message" in last:
                low = last["user_message"].lower()
                if any(w in low for w in ["sad", "unhappy", "hurt", "sick", "scared"]):
                    response_candidates = AFFECTION + response_candidates
    except Exception:
        pass

    # Pick random response and sanitize
    global _last_response  # module-level variable to store last response
    try:
        _last_response
    except NameError:
        _last_response = None

    candidates = response_candidates if response_candidates else DEFAULT_RESPONSES

    # Avoid repeating the same response consecutively
    resp = random.choice(candidates)
    if resp == _last_response and len(candidates) > 1:
        filtered = [r for r in candidates if r != _last_response]
        resp = random.choice(filtered)

    _last_response = resp  # remember it for next call

    resp = html.escape(resp)  # avoid weird characters
    # Trim to about 120 chars to keep UI clean
    if len(resp) > 180:
        resp = resp[:177].rstrip() + "..."
    return resp


# compatibility alias in case other code calls this name
def generate_pet_response(user_message: str, pet_status: Optional[Dict] = None, context: Optional[List[Dict]] = None) -> str:
    return send_message(user_message, pet_status=pet_status, context=context)

def test_ai_connection() -> str:
    """
    Simple stub so sqlite_main_app.py doesn't crash.
    Returns a fake "connection successful" message.
    """
    return "AI client is ready (offline mode)."

# Expose API
__all__ = ["send_message", "generate_pet_response", "test_ai_connection"]

