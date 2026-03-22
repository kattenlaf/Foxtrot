# Some constants for the json resources file
TOKEN = "TOKEN"

MEMBER_PROFILES = "profiles"
MEMBER_PROFILE_SOUND_EXIT = "exit_sound"
MEMBER_PROFILE_SOUND_ENTER = "enter_sound"

# OTHER CONSTANTS
DEFAULT = "default"
JARVIS_CMD_PREFIX = "!"
DISCORD_RESOURCES = "discord_resources.json"

LOCAL_SOUNDS = "C:\\Users\\ruelg\\PycharmProjects\\Foxtrot\\.venv\\static\\mp3"

SOUND_TYPE_ENTER = 0
SOUND_TYPE_EXIT = 1
SOUND_TYPES = {
    SOUND_TYPE_ENTER : MEMBER_PROFILE_SOUND_ENTER,
    SOUND_TYPE_EXIT : MEMBER_PROFILE_SOUND_EXIT
}

# Todo build this programmatically
# scan directory with the files and just load in the names and path to the dictionary

# Sound effects
FAAAH = f"{LOCAL_SOUNDS}\\faaah.mp3"
ALERT = f"{LOCAL_SOUNDS}\\alert.mp3"
SAILOR_MOON = f"{LOCAL_SOUNDS}\\sailor_moon.mp3"
POKEBALL = f"{LOCAL_SOUNDS}\\pokeball.mp3"
PLUG = f"{LOCAL_SOUNDS}\\plug.mp3"
DEFAULT_SOUND_EFFECT = f"{LOCAL_SOUNDS}\\faaah.mp3"
# --------------------------------
# look up for sounds
SOUNDS_AVAILABLE = {
    "default": DEFAULT_SOUND_EFFECT,
    "faaah" : FAAAH,
    "alert" : ALERT,
    "sailor_moon" : SAILOR_MOON,
    "plug" : PLUG,
    "pokeball" : POKEBALL
}

# JSON CONSTANTS
JSON_SOUND = "sound"

DEFAULT_VOLUME = 0.5
CHECK_MESSAGE_LIMIT = 100

