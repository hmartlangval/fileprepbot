from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv

load_dotenv()

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        
    async def generate_response(self, message):
        return "I am LLM Bot"
    
    
bot = MainBot(options={
    "bot_id": "fileprep",
    "bot_name": "Fileprep Service",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "prompts/datacollection.txt"
})

bot.start();


import requests
import json
def call_rest_api():
    json_data = {
        "order_number": "73-832-8383",
        "s_data": {
            "x_account_number": "1234567890",
            "x_county": "brevard"
        }
    }
    data = {
        "content": f"@fileprep start processing for [json]{json.dumps(json_data)}[/json]",
        "sender": "Admin"
    }
    try:
        response = requests.post('http://localhost:3000/api/channels/general/sendMessage', json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()  # Return the response as JSON
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
call_rest_api()

bot.join();

bot.cleanup();

