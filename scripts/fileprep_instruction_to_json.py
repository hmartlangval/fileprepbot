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

async def preprocessing_tasks(self, context):
    """ Purpose is to ensure that we parse the instruction prompt file in the way we want it. No mistake should happen in prompt"""
    print('initializing on the test browser client')
    
    session_data = context.SessionData
    json_data = session_data.get('json_data', {})
    sensitive_data = self.extract_sensitive_data(json_data)
    self.create_download_folder(json_data)
    

async def prepare_prompt_json(self, context):
    """ Purpose is to ensure that we parse the instruction prompt file in the way we want it. No mistake should happen in prompt"""
    print('initializing on the test browser client')
    
    session_data = context.SessionData    
    prompt_text = session_data.get('instructions', '')
    
    prompt_data = {}
    current_county = None

    in_instructions = False
    instructions = []
    
    for line in prompt_text.split('\n'):
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

async def get_instructions(self, context):
    session_data = context.SessionData
    sensitive_data = session_data.get('sensitive_data', {})
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
    
    session_data['instructions'] = instructions
    # return instructions