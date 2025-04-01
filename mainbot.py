from base_bot.llm_bot_base import LLMBotBase
from dotenv import load_dotenv
from classes.pdf_to_image import PdfToImage
import json

load_dotenv()

class MainBot(LLMBotBase):
    def __init__(self, options, *args, **kwargs):
        super().__init__(options, *args, **kwargs)
        self.isBusy = False
        
    async def process_tasks(self, message, tasks):
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@taxbot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@propertybot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"@mapbot start processing for [json]{json.dumps(tasks)}[/json]"
        })
        print('All tasks initiated for ', tasks)
        self.socket.emit('message', {
            "channelId": message.get("channelId", "general"),
            "content": f"All Tasks initiated for order: {tasks.get('order_number', 'n/a')}"
        })
        # for task in tasks:
        #     url = task.get("url", None)
        #     print('url exists', url)
        #     if url:
        #         url = f"http://localhost:3000{url}"
        #         print('url exists', url)
        #         pdf = requests.get(url)
        #         # print('pdf exists', pdf)
        #         if pdf:
        #             # Save the PDF content to a temporary file
        #             from io import BytesIO
        #             # print('pdf content exists', pdf.content)
        #             pdf_buffer = BytesIO(pdf.content)
        #             print('pdf content is now in buffer')
                    
        #             # # Prepare instructions for LLM
        #             instructions = "Extract content and return formatted data from the provided PDF."
                    
        #             # # Call the LLM agent to process the PDF
        #             result = await self.call_agent(instructions, pdf_buffer)
                    
        #             print('extraction result', result)
        #             # # Handle the result as needed
        #             self.socket.emit('message', {
        #                 "channelId": message.get("channelId"),
        #                 "content": f"Task completed. Extracted data: ..."
        #             })
                    
        #             # Clean up the temporary file
        #             # os.remove(temp_pdf_path)
    
    async def generate_response(self, message):
        if(self.isBusy):
            return "I am currently busy. Please wait for me to finish the task."
        
        def emit_start_message(message):
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": 'Message is received, processing... Allow me to finish the task first >>>'
            })
          
        json_data = super().extract_json_data(message)
        
        action = None
        if json_data:
            action = json_data.get("action", None)
          
        if action == "start_local_pdf":
            emit_start_message(message)
            self.isBusy = True
            try:
                data = json_data.get("data", [])
                
                for item in data:
                    userInput_json = None
                    pdf_path = item.get("pdf_path", None)
                    if pdf_path:
                        instructions = await self.quick_load_prompts("prompts/pdf_extraction.txt")
                        instructions = instructions.replace("[order_number]", PdfToImage.get_file_name_from_path(item.get("original_filename", "ai-do-not-fill")))
                        
                        if pdf_path.startswith("http"):
                            extracted_data = PdfToImage.pdf_page_to_base64_from_url(pdf_path)
                            result = await self.analyze_image(instructions, encoded_image_base64=extracted_data)
                            clean_parsed = result.replace("```json", "").replace("```", "")
                            userInput_json = json.loads(clean_parsed)
                            userInput = "PDF has been analyzed from URL {}. Result: [json]{}[/json]".format(pdf_path, clean_parsed)
                        else:
                            extracted_data = PdfToImage.pdf_page_to_base64_from_path(pdf_path)
                            result = await self.analyze_image(instructions, encoded_image_base64=extracted_data)
                            clean_parsed = result.replace("```json", "").replace("```", "")
                            userInput_json = json.loads(clean_parsed)
                            userInput = "PDF has been analyzed from local path {}. Result: [json]{}[/json]".format(pdf_path, clean_parsed)
                    
                        if userInput_json:
                            await self.process_tasks(message, userInput_json)
                    else:
                        return "You seem to have not provided a valid pdf path"
                
                return "Request Processed"
            finally:
                self.isBusy = False
                print("Processing complete, busy status reset to False")
        
        elif action == "start_task":
            data = json_data.get("data", {})
            
            self.socket.emit('message', {
                "channelId": message.get("channelId"),
                "content": f"Request Accepted. Starting Tasks for the following [json] {json.dumps(data)} [/json]"
            })
            
            await self.process_tasks(message, data)
            
            return f"Tasks started!!"
     
        
        print(message)
        
        self.isBusy = False
        return f"""Hello {message.get("senderName", "Guest")}, I am currently trained to help you automate a task. I cannot offer any other services.
            To start a task, click on the "Start Task" button on the top right of the screen.
        """

        # elif action is not None:
        #     return "I am instructed to perform task i am not trained on. Task: " + json_data.get("action", "unknown")
        
        # return "I am a simple FilePrep Service Bot"
    
    
bot = MainBot(options={
    "bot_id": "fileprep",
    "bot_name": "Fileprep Service",
    "autojoin_channel": "general",
    "model": "gpt-4o-mini",
    "prompts_path": "prompts/datacollection.txt"
})

bot.start()


# import requests
# import json
# def call_rest_api():
#     json_data = {
#         "action": "start_local_pdf",
#         "data": [
#             {
#                 "pdf_path": "D:/cursor/fileprep_prod/fileprepbot/23-930-2323.pdf",
#                 "original_filename": "23-930-2323.pdf",
#                 "file_type": "application/pdf"
#             }
#         ]
#     }
#     # json_data = {
#     #     "action": "start_task",
#     #     "data": [
#     #         {
#     #             "pdf_path": "/api/data/1743192045452-Doc1.pdf",
#     #             "original_filename": "Doc1.pdf",
#     #             "file_type": "application/pdf",
#     #             "data_id": "1743192045452-Doc1.pdf",
#     #             "folder_path": "aido_order_files",
#     #             "createdAt": "2025-03-28T20:00:48.455Z",
#     #             "updatedAt": "2025-03-28T20:00:48.455Z",
#     #             "isActive": True,
#     #             "_id": "67e6fff0777548eec1631ebe"
#     #         }
#     #     ]
#     # }
#     # json_data = {
#     #     "action": "start_task",
#     #     "data": [
#     #         {
#     #             "order_number": "Doc1",
#     #             "s_data": {
#     #                 "x_county": "Pasco",
#     #                 "x_property_address": "3501 Zoyla Dr, New Port Richey, FL 34653",
#     #                 "x_account_number": "",
#     #                 "x_house_number": "3501",
#     #                 "x_street_name": "Zoyla Dr",
#     #                 "x_city": "New Port Richey",
#     #                 "x_zip_code": "34653"
#     #             }
                
#     #         }
#     #     ]
#     # }
#     data = {
#         "content": f"@fileprep start processing for [json]{json.dumps(json_data)}[/json]",
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

bot.join()

bot.cleanup()

