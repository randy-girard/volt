import re

class RegexEngine():
    def __init__(self, profile=None):
        self.profile = profile
        self.expression = None
        self.replace_char = ""
        self.m = None

    def compile(self, text):
        # Clean up some weirdness
        text = text.replace("^{", "{")

        matches = re.findall("\{([A-Za-z][0-9]?)\}", text)
        if len(set(matches)) == 1 and len(matches) > 1:
            self.replace_char = matches[0]
            for index, match in enumerate(matches):
                text = text.replace(f"{{{match}}}", f"(?<{match}{index+1}>.+)", 1)

        # Find all the {X} style tags and convert them
        for index, match in enumerate(re.findall("\{([A-Za-z][0-9]?)\}", text)):
            text = text.replace(f"{{{match}}}", f"(?<{match}>.+)", 1)

        # Fix for newer perl regex stuff
        text = text.replace("?<", "?P<")

        self.expression = re.compile(text, re.IGNORECASE)

    def match(self, text):
        self.m = re.search(self.expression, text)
        return self.m

    def execute(self, text, matches=None):
        counts = {}

        if text and len(text) > 0:
            # Standardize the {X} tags
            text = text.replace("^{", "{")
            text = text.replace("${", "{")

            # Replace integer only match tags
            for index, match in enumerate(re.findall("\{([0-9]?)\}", text)):
                text = text.replace(f"{{{match}}}", f"{{{self.replace_char}{match}}}", 1)

            # Replace the matches
            match_keys = self.expression.groupindex.keys()
            if match_keys:
                for key in list(match_keys):
                    if matches:
                        group_key = matches.group(key)
                        text = text.replace(f"{{{key}}}", group_key or "")
                    else:
                        pass
            elif matches:
                # Replace the regex regular match groups
                for index, match in enumerate(matches.groups()):
                    text = text.replace(f"{{{index + 1}}}", match)

        if self.profile:
            text = text.replace("{C}", self.profile.name)

        return text
