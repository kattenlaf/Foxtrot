import discord
import constants
import json

# Todo check this works
def GetResources():
    file_abs_path = os.path.abspath(os.path.dirname(__file__))
    resources_path = os.path.join(file_abs_path, '..', 'resources.json')
    with open(resources_path, 'r') as f:
        file_data = f.read()
        resources_data = json.loads(file_data)
    return resources_data

def GetBotToken(resources):
    return resources[constants.TOKEN]

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message: discord.Message):
        if message.author != self.user:
            print(f'Message from {message.author}: {message.content}')

        if message.content.startswith('foo'):
            await message.channel.send('boo')

class Jarvis:
    def __init__(self):
        self.intents = discord.Intents.default()
        self.client = None
        self.bot_resources = GetResources()
        self.token = GetBotToken(self.bot_resources)

    def RunClient(self):
        self.client = Client(intent=self.intents)
        self.client.run(self.token)

    def ParseMessageContent(self):
        self.intents.message_content = True
        self.RunClient()

jarvis = Jarvis()
jarvis.ParseMessageContent()