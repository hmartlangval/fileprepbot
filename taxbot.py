from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import AbstractBot
 
load_dotenv()
 
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
       
        ## do validation if it should proceed or not based on json data ONLY IF REQUIRED
        if json_data.get('x_county') == 'nelvin':
            return "I reject because i cannot serve nelvin county"
       
        [instructions, sensitive_data, extend_system_prompt] = await super().prepare_LLM_data(json_data, message)
       
        print(f"instructions: {instructions}")
        print(f"sensitive_data: {sensitive_data}")
        print(f"extend_system_prompt: {extend_system_prompt}")
       
        result  = await self.call_agent(instructions, extend_system_message=extend_system_prompt, sensitive_data=sensitive_data)
<<<<<<< HEAD
        
        return "I am Tax Bot. Task has been completed."
=======
        summary = self.analyse_summary(result)
        return f"I am Tax Bot. Taks has been completed. {summary}"
>>>>>>> 5832678656c207ba63ab646fc5d6cdb5f0c224ed
    
    def analyse_summary(self, summary):
        prompt = f""" You are provided with summary of task that has been completed.
        Please analyse the summary :
        {summary}
 
        and provide the result in short format using max 20 words."""
        llm = ChatOpenAI(model="gpt-4-turbo")

bot = TaxBot(options={
    "bot_id": "taxbot",
    "bot_name": "TaxBot",
    "bot_type":"task_bot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
<<<<<<< HEAD
    "prompts_path": "prompts/tax_steps.txt",
    "system_prompt_path": "prompts/tax_system.txt",
    # "downloads_path": "my_download_path"
    "downloads_path": r"D:/browser_use_bot/fileprepbot/downloads"
=======
    "prompts_path": "./prompts/tax_steps.txt",
    "system_prompt_path": "./prompts/tax_system.txt",
    # "downloads_path": r"D:\ThoughtfocusRD\Phase_2_navigators_deo\Base_bot\fileprepbot\downloads"
>>>>>>> 5832678656c207ba63ab646fc5d6cdb5f0c224ed
})
 
bot.start()
bot.join()
bot.cleanup()