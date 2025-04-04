from base_bot.browser_client_base_bot import BrowserClientBaseBot
from dotenv import load_dotenv
import os

load_dotenv()

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

class FilePreparationParentBot(BrowserClientBaseBot):
    def __init__(self, options=None, *args, **kwargs):
        
        if options is None:
            options = {}
        
        downloads_path = options.get("downloads_path", None)
        if not downloads_path:
            downloads_path = os.getenv("DOWNLOADS_PATH", None)
            if downloads_path:
                options.setdefault("downloads_path", downloads_path)
        
        super().__init__(options, *args, **kwargs)
        self.variables = [
            "order_number", # non sensitive data, ok to be sent to LLM
            "x_county", # count is also OK to be sent to LLM
        ]
        
    def create_download_folder(self, json_data):
        if json_data:
            order_number = json_data.get("order_number")
            if order_number:
                new_dl_path = self.create_custom_downloads_directory(order_number)
                print("downloads path:", new_dl_path)
                
    async def prepare_prompt_json(self):
        """ Purpose is to ensure that we parse the instruction prompt file in the way we want it. No mistake should happen in prompt"""
        print('initializing on the test browser client')
        
        prompt_data = {}
        current_county = None

        in_instructions = False
        
        for line in self.prompt_text.split('\n'):
            line = line.strip()

            if line.startswith("#"):
                continue                
            if line.startswith(">>County:") and not in_instructions:
                current_county = line.replace('>>County:', '').strip()
                prompt_data[current_county] = {}
                in_instructions = False
            elif line.startswith(">>URL:"):
                url = line.replace('>>URL:', '').strip()
                prompt_data[current_county]['url'] = url
            elif line.startswith(">>INSTRUCTIONS:"):
                instructions = []
                in_instructions = True
            elif in_instructions:
                if line.startswith(">>County:"):
                    if current_county and instructions:
                        prompt_data[current_county]['instructions'] = "\n".join(instructions)
                    current_county = line.replace('>>County:', '').strip()
                    prompt_data[current_county] = {}
                    in_instructions = False
                else:
                    instructions.append(line.strip())
            elif line == "":
                continue
            else:
                instructions.append(line.strip())

        if current_county and instructions:
            prompt_data[current_county]['instructions'] = "\n".join(instructions)

        self.prompt_json = prompt_data
        print('prompt json file is loaded and is ready to use')
    
    def extract_sensitive_data(self, json_data):
        if json_data:
            s_data = json_data.get('s_data', {})
        else:
            s_data = {}
        return s_data
    
    def get_instructions(self, json_data, sensitive_data):
        county = sensitive_data.get('x_county').lower()
        if county:
            county = county.lower()
            county_code = next((key for key, value in countyMap.items() if value.lower() == county), None)
            if county_code:
                sensitive_data['x_county'] = county_code
            else:
                sensitive_data['x_county'] = county.lower()
            prompt_data = self.prompt_json.get(county, {})
            navigate_url = prompt_data.get('url', '')
            instructions = prompt_data.get('instructions', '')
        else:
            instructions = ''
            
        if not instructions or not navigate_url:
            return None
            
        instructions = f"""
        search_by_account_number: {'true' if sensitive_data.get('x_account_number') else 'false'}
        
        Navigate to the following URL: {navigate_url}
        
        {instructions}        
        """        
        
        for variable in self.variables:
            instructions = instructions.replace(f'[{variable}]', json_data.get(variable, ''))
            
        return instructions
    
    async def prepare_LLM_data(self, json_data, message):
        sensitive_data = self.extract_sensitive_data(json_data)
        
        # you can do if all data is valid or not
        self.create_download_folder(json_data)
        
        if not self.is_prompt_loaded:
            # self.socket.emit('message', {
            #     "channelId": message.get("channelId"),
            #     "content": 'Message is received, processing... >>>'
            # })

            await self.load_prompts()
            await self.prepare_prompt_json()
            
        instructions = self.get_instructions(json_data, sensitive_data)
       
        print(instructions)
        
        try:
            spp = self.options.get('system_prompt_path', None)
            if spp:
                with open(spp, 'r') as file:
                    extend_system_prompt = file.read()
                    for variable in self.variables:
                        extend_system_prompt = extend_system_prompt.replace(f'[{variable}]', json_data.get(variable, ''))
            else:
                extend_system_prompt = ""
        except FileNotFoundError:
            extend_system_prompt = "Error: The file 'prompts/property_appraisal_system.txt' was not found."
        except Exception as e:
            extend_system_prompt = f"An error occurred while reading the file: {e}"

        
        return [instructions, sensitive_data, extend_system_prompt]


