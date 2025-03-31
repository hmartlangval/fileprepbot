import asyncio
import json
from base_bot.browser_client_base_bot import BrowserClientBaseBot
from dotenv import load_dotenv

load_dotenv()

class TestBot(BrowserClientBaseBot):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        
bot = TestBot(options={
    "bot_id": "tb",
    "bot_name": "TestBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "prompts/datacollection.txt",
    # "browser_headless": True
})

bot.start();

async def test_bot():
    # test with simple prompt
    result = await bot.call_agent("What is the capital of the United States?")
    print('Test completed with result', result)
    
    # test without any instructions, it should return "No instructions provided"
    # result = await bot.call_agent("")
    # print('test result', result)
    
asyncio.run(test_bot())


bot.join();

bot.cleanup();

