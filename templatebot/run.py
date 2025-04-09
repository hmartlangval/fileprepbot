import json
from dotenv import load_dotenv
import AbstractBot
from langchain_openai import ChatOpenAI
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
       
        for action in await self.actions_in_config():
            [instructions, sensitive_data, extend_system_prompt] = await super().prepare_LLM_data(json_data, message, action)
            
            # instructions_result = await self.analyze_instructions(instructions)

            # self.socket.emit('message', {
            #     "channelId": message.get("channelId"),
            #     "content": instructions_result
            # })
        
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
                                                    "annual_pdf_filename": "anything.pdf",
                                                    "original_json": json_data
                                                })
                [is_success, final_summary] = self.check_success_or_failure(result)
                if is_success:
                    result_text = await self.format_output(action, final_summary)
                else:
                    result_text = f"Action '{action['name']}' has failed. Message: {final_summary}"
            else:
                combined_instructions = f"""
                {extend_system_prompt}
                
                {instructions}
                """
                result = await self.call(combined_instructions)
                result_text = await self.format_output(action, result)
                
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": result_text
            })

        return "Action executor exited."
    
    # async def analyse_summary(self, summary):

    #     prompt = f""" You are provided with summary of task that has been completed.
    #     Please analyse the summary :
    #     {summary}       
    #     **If pdf was downloaded or not, if any errors occurred or not.
    #     **Also give the download path where the files were downloaded.
    #     ** provide the result in short format using max 20 words.
    #     ** If the summary is not provided then return "No summary provided"
    #     """

    #     llm = ChatOpenAI(model="gpt-4-turbo")
    #     result = llm.invoke(prompt)
    #     return result.content
    
bot = TaxBot(options={
    "window_handle": get_window_handle(),
    "bot_type": "task_bot",
    "bot_id": "templatebot",
    "bot_name": "TemplateBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_directory": "prompts",
    # "prompts_path": "./prompts/taxbot/tax_steps.txt",
    # "system_prompt_path": "./prompts/tax_system.txt"
})
 
bot.start()

bot.join()
bot.cleanup()