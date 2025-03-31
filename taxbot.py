from dotenv import load_dotenv

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
        
        return "I am Property Bot. Taks has been completed."
    
    
bot = TaxBot(options={
    "bot_id": "taxbot",
    "bot_name": "TaxBot",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "prompts/tax_steps.txt",
    "system_prompt_path": "prompts/tax_system.txt",
    # "downloads_path": "my_download_path"
    "downloads_path": "E:/testingdownload"
})

bot.start();


# import requests
# import json
# def call_rest_api():
#     json_data = {
#         "order_number": "73-832-8383",
#         "s_data": {
#             'x_account_number': '322S22004900800010', 
#             'x_county': 'baker', 
#             'x_property_address': '362 MINNESOTA AVE E MACCLENNY'
#         }
#     }
    
#     # json_data = {
#     #     "order_number": "73-832-8383",
#     #     "s_data": {
#     #         'x_parcel_id': '01-4S-02W-000-01807-002', 
#     #         'x_county': 'wakulla', 
#     #         'x_property_address': '239 HARVEY MILL RD CRAWFORDVILLE 32327'
#     #     }
#     # }
#     #Brevard
#         # sensitive_data = {
#         #     'x_county': 'brevard','x_account_number': '010089000', 'x_property_address': 'STONEWOOD TOWNHOMES LLC, 325 E UNIVERSITY BLVD #81'
#         # }
    
#     data = {
#         "content": f"@taxbot Welcome!! [json]{json.dumps(json_data)}[/json]",
#         "sender": "Admin"
#     }
#     try:
#         response = requests.post('http://localhost:3000/api/channels/general/sendMessage', json=data)
#         response.raise_for_status()  # Raise an error for bad status codes
#         return response.json()  # Return the response as JSON
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")
#         return None
# call_rest_api()




bot.join();

bot.cleanup();

