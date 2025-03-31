import asyncio
import json
import sys
import os
from dotenv import load_dotenv
from base_bot.llm_bot_base import LLMBotBase


# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.pdf_to_image import PdfToImage
from classes.utils import clean_json_string

load_dotenv()

class TestBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        
bot = TestBot(options={
    "bot_id": "tb",
    "bot_name": "TestBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "prompts/datacollection.txt",
})

bot.start();

async def test_bot():
    
    # pdf_path = 'C:\\Users\\nelvi\\Desktop\\AI-DO\\test\\WTS-25-000016 Order.pdf'
    # text = PdfToImage.extract_text_from_pdf(pdf_path)
    
    pdf_url = 'http://localhost:3000/api/data/1743430963340-WTS-25-000114 Order.pdf'
    text = PdfToImage.extract_text_from_pdf(pdf_url)
    # print('text', text)
    # test with simple prompt
    
    # test without any instructions, it should return "No instructions provided"
    # result = await bot.call_agent("")
    # print('test result', result)
    
    prompt = await bot.quick_load_prompts("prompts/pdf_text_extraction.txt")
    instructions = f"{prompt}. \n\n Text extracted from PDF: {text}"
    instructions = instructions.replace("[order_number]", "WTS-25-000114")
    result = await bot.call(instructions)
    result = clean_json_string(result)
    print(result)
    
asyncio.run(test_bot())


bot.join();

bot.cleanup();

