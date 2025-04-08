async def prepare_prompt_json(self):
    """ Purpose is to ensure that we parse the instruction prompt file in the way we want it. No mistake should happen in prompt"""
    print('initializing on the test browser client')
    
    # __self = self.__self
    prompt_text = self.prompt_text or ""
    
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
    