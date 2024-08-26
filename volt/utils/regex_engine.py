import re

class RegexEngine():
    def __init__(self, profile=None):
        self.profile = profile
        self.expression = None
        self.duration = None
        self.replace_char = ""
        self.m = None

    def compile(self, text):
        # Clean up some weirdness
        text = text.replace("^{", "{")
        text = text.replace("${", "{")

        matches = re.findall("\{([A-Za-z][0-9]?)\}", text)

        if len(set(matches)) == 1 and len(matches) > 1:
            self.replace_char = matches[0]
            for index, match in enumerate(matches):
                text = text.replace(f"{{{match}}}", f"(?<{match}{index+1}>.+)", 1)

        # Find all the {X} style tags and convert them
        for index, match in enumerate(re.findall("\{([A-Za-z][0-9]?)\}", text)):
            text = text.replace(f"{{{match}}}", f"(?<{match}>.+)", 1)

        # Replace timestamp matcher
        text = text.replace("{ts}", "(?<timestamp>.+)")
        text = text.replace("{TS}", "(?<timestamp>.+)")

        # Fix for newer perl regex stuff
        text = text.replace("?<", "?P<")

        try:
            self.expression = re.compile(text, re.IGNORECASE)
        except Exception as e:
            self.expression = re.compile(re.escape(text), re.IGNORECASE)


    def match(self, text):
        self.m = re.search(self.expression, text)
        return self.m

    def to_seconds(self, timestr):
        seconds= 0
        for part in timestr.split(':'):
            seconds= seconds*60 + int(part, 10)
        return seconds

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
                for index, key in enumerate(list(match_keys)):
                    if matches:
                        group_key = matches.group(key)

                        if key == "timestamp":
                            self.duration = self.to_seconds(group_key)

                        text = text.replace(f"{{{key}}}", group_key or "")
                        text = text.replace(f"{{{index + 1}}}", group_key or "")
                    else:
                        pass

            start_index = len(match_keys)
            if matches:
                # Replace the regex regular match groups
                for index, match in enumerate(matches.groups()):
                    if match:
                        text = text.replace(f"{{{index + 1}}}", match)
                        text = text.replace(f"{{{self.replace_char}{index + 1}}}", match)

            if self.profile:
                text = text.replace("{C}", self.profile.name)
                text = text.replace("{c}", self.profile.name)

        return text
