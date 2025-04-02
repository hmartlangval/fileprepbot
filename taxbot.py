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
        summary = self.analyse_summary(result)
        return f"I am Tax Bot. Taks has been completed. {summary}"
    
    def analyse_summary(self, summary):
        prompt = f""" You are provided with summary of task that has been completed.
        Please analyse the summary :
        {summary}
 
        and provide the result in short format using max 20 words."""
        llm = ChatOpenAI(model="gpt-4-turbo")

bot = TaxBot(options={
    "bot_id": "taxbot",
    "bot_name": "TaxBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "./prompts/tax_steps.txt",
    "system_prompt_path": "./prompts/tax_system.txt",
    # "downloads_path": r"D:\ThoughtfocusRD\Phase_2_navigators_deo\Base_bot\fileprepbot\downloads"
})
 
bot.start()
bot.join()
bot.cleanup()