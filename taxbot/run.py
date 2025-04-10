import json
import os
from dotenv import load_dotenv
import AbstractBot
from langchain_openai import ChatOpenAI

from classes.bot_helper import format_output
load_dotenv()

import ctypes

def get_window_handle():
    user32 = ctypes.windll.user32
    handle = user32.GetForegroundWindow()
    return handle

class TaxBot(AbstractBot.FilePreparationParentBot):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
   
    async def generate_response(self, message):
       
        self.socket.emit('message', {
            "channelId": message.get("channelId"),
            "content": 'Message is received, processing... >>>'
        })
       
        ## only customization here
        json_data = super().extract_json_data(message)
        order_number = json_data.get('order_number', None)
        if not order_number:
            raise Exception("Order Number is None")
       
        for action in await self.actions_in_config():
            [instructions, sensitive_data, extend_system_prompt] = await super().prepare_LLM_data(json_data, message, action)
            
            print(f"instructions:       {instructions}")
            print(f"sensitive_data:          {sensitive_data}")
            print(f"extend_system_prompt:  {extend_system_prompt}")
            
            if not instructions:
                self.socket.emit('message', {
                    "channelId": message.get("channelId"),
                    "content": f"Action '{action['name']}' has No instructions provided."
                })
                continue
        
            # output_formatting = action.get('output_formatting', 'text')
            if action.get('requires_browser', False):
                result  = await self.call_agent(instructions, extend_system_message=extend_system_prompt, sensitive_data=sensitive_data,
                                                session_config={
                                                    "annual_pdf_filename": f"{order_number}-Tax.pdf",
                                                    "original_json": json_data
                                                })
                [is_success, final_summary] = self.check_success_or_failure(result)
                if is_success:
                    result_text = await format_output(self.script_executor, action, final_summary)
                else:
                    result_text = f"Action '{action['name']}' for order '{order_number}' has failed. Message: {final_summary} [json]{json.dumps(json_data)}[/json] [Retry]"
            else:
                combined_instructions = f"""
                {extend_system_prompt}
                
                {instructions}
                """
                result = await self.call(combined_instructions)
                result_text = await format_output(self.script_executor, action, result)
                
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": result_text
            })

        return "Action executor exited."
    
bot = TaxBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "task_bot",
    "bot_id": "taxbot",
    "bot_name": "TaxBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_directory": os.getenv("PROMPTS_DIR_PATH", "prompts"),
})
 
bot.start()

bot.join()
bot.cleanup()