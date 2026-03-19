# Some constants for the json resources file
TOKEN = "TOKEN"

MEMBER_PROFILES = "profiles"
MEMBER_PROFILE_SOUND = "sound"

# OTHER CONSTANTS
DEFAULT = "default"
JARVIS_CMD_PREFIX = "!"
DISCORD_RESOURCES = "discord_resources.json"

LOCAL_SOUNDS = "C:\\Users\\ruelg\\PycharmProjects\\Foxtrot\\.venv\\static\\mp3"

# Sound effects
FAAAH = f"{LOCAL_SOUNDS}\\faaah.mp3"
ALERT = f"{LOCAL_SOUNDS}\\alert.mp3"
SAILOR_MOON = f"{LOCAL_SOUNDS}\\sailor_moon.mp3"
DEFAULT_SOUND_EFFECT = f"{LOCAL_SOUNDS}\\faaah.mp3"
# --------------------------------
# look up for sounds
SOUNDS_AVAILABLE = {
    "default": DEFAULT_SOUND_EFFECT,
    "faaah" : FAAAH,
    "alert" : ALERT,
    "sailor_moon" : SAILOR_MOON
}

# JSON CONSTANTS
JSON_SOUND = "sound"

DEFAULT_VOLUME = 0.5
CHECK_MESSAGE_LIMIT = 100

