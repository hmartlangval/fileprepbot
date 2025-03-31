import os
from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv
import json
import asyncio

load_dotenv()

SubtaskType = {
    'MAP': 'map',
    'TAX': 'tax',
    'PROPERTY': 'property'
}

BotNames = {
    SubtaskType['MAP']: 'map_bot',
    SubtaskType['TAX']: 'tax',
    SubtaskType['PROPERTY']: 'property_bot'
}

countyMap = {
    "alachua": "Alachua",
    "baker": "Baker",
    "bay": "Bay",
    "bradford": "Bradford",
    "brevard": "Brevard",
    "broward": "Broward",
    "calhoun": "Calhoun",
    "charlotte": "Charlotte",
    "citrus": "Citrus",
    "clay": "Clay",
    "collier": "Collier",
    "columbia": "Columbia",
    "desoto": "DeSoto",
    "dixie": "Dixie",
    "duval": "Duval",
    "escambia": "Escambia",
    "flagler": "Flagler",
    "franklin": "Franklin",
    "gadsden": "Gadsden",
    "gilchrist": "Gilchrist",
    "glades": "Glades",
    "gulf": "Gulf",
    "hamilton": "Hamilton",
    "hardee": "Hardee",
    "hendry": "Hendry",
    "hernando": "Hernando",
    "highlands": "Highlands",
    "hillsborough": "Hillsborough",
    "holmes": "Holmes",
    "indian_river": "Indian River",
    "jackson": "Jackson",
    "jefferson": "Jefferson",
    "lafayette": "Lafayette",
    "lake": "Lake",
    "lee": "Lee",
    "leon": "Leon",
    "levy": "Levy",
    "liberty": "Liberty",
    "madison": "Madison",
    "manatee": "Manatee",
    "marion": "Marion",
    "martin": "Martin",
    "miami-dade": "Miami-Dade",
    "monroe": "Monroe",
    "nassau": "Nassau",
    "okaloosa": "Okaloosa",
    "okeechobee": "Okeechobee",
    "orange": "Orange",
    "osceola": "Osceola",
    "palm_beach": "Palm Beach",
    "pasco": "Pasco",
    "pinellas": "Pinellas",
    "polk": "Polk",
    "putnam": "Putnam",
    "santa_rosa": "Santa Rosa",
    "sarasota": "Sarasota",
    "seminole": "Seminole",
    "st_johns": "St Johns",
    "st_lucie": "St Lucie",
    "sumter": "Sumter",
    "suwannee": "Suwannee",
    "taylor": "Taylor",
    "union": "Union",
    "volusia": "Volusia",
    "wakulla": "Wakulla",
    "walton": "Walton",
    "washington": "Washington"
}

class MMBot(LLMBotBase):
    def __init__(self, options=None, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        
        self.conversations = {}
        self.userTasks = {}

    async def generate_response(self, message):
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Data collector starting up...'
        })
        
        if not self.is_prompt_loaded:
            await self.load_prompts()
                
        userId = message['senderId']
        channelId = message['channelId']
        userInput = message['content']

        if userId not in self.userTasks:
            self.userTasks[userId] = {
                'taskId': self.generateTaskId(),
                'subTasks': [],
                'status': 'idle'
            }
            
        userTask = self.userTasks[userId]

        if userId not in self.conversations:
            self.conversations[userId] = [
                {"role": "system", "content": self.prompt_text.replace('{user_id}', userId).replace('{status}', userTask['status'])}
            ]
        conversation = self.conversations[userId]

        if userInput.lower() in ["cancel", "stop"]:
            
            self.conversations[userId] = [
                {"role": "system", "content": self.prompt_text}
            ]
            userTask['status'] = 'cancelled'
            return "Task cancelled."

        conversation.append({"role": "user", "content": userInput})

        try:
            response = await self.call(conversation)
            responseContent = response

            # responseContent = response.choices[0].message['content']
            jsonResponse = self.extractJsonBlock(response)
            if jsonResponse:
                county = jsonResponse['county']
                county_code = next((key for key, value in countyMap.items() if value == county), None)
                if county_code:
                    jsonResponse['sensitive_data']['x_county'] = county_code
                else:
                    jsonResponse['sensitive_data']['x_county'] = county.lower()

                asyncio.create_task(self.requestProcessing(userId, channelId, jsonResponse))

                return f"Here is the JSON response: [json]{json.dumps(jsonResponse)}[/json]"
            else:
                self.userTasks[userId]['status'] = 'in progress'

            conversation.append({"role": "assistant", "content": responseContent})

            if len(conversation) > 20:
                self.conversations[userId] = [conversation[0]] + conversation[-19:]

            return responseContent
        except Exception as error:
            print("Error calling OpenAI:", error)
            return "I'm sorry, I encountered an error processing your request. Please try again."

    def generateTaskId(self):
        import uuid
        return str(uuid.uuid4())

    async def requestProcessing(self, userId, channelId, jsonResponse):
        await asyncio.sleep(0.2)
        print("JSON RESPONSE RECEIVED.. now calling all 3 tasks")
        print("starting tax processing")
        await self.requestTask(userId, channelId, BotNames[SubtaskType['TAX']], jsonResponse)
        print("starting property processing")
        await self.requestTask(userId, channelId, BotNames[SubtaskType['PROPERTY']], jsonResponse)
        print("starting map processing")
        await self.requestTask(userId, channelId, BotNames[SubtaskType['MAP']], jsonResponse)

    async def requestTask(self, requestorUserId, channelId, botId, jsonResponse):
        message = f"@{botId} Process Details using the following address: {jsonResponse['address']}.\n[json]{json.dumps(jsonResponse, indent=2)}[/json]"
        self.socket.emit('message', {
            'channelId': channelId,
            'content': message
        })
        print(f"Requested processing for user {requestorUserId}")

bot = MMBot(options={
    'bot_id': 'a',
    'bot_name': 'Fileprep Data',
    'bot_type': 'server',
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    'prompts_path': 'prompts/datacollection.txt',
})

bot.start();
# @bot.on('connected')
# def on_connected(message):
#     print('Connected to server, autojoining channel "general"')
#     bot.processCommand('/join general')


bot.join();

bot.cleanup();
