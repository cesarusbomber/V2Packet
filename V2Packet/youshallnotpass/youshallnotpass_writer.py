import os
import random

# Text that gets written into files
BASE_TEXT = """Hello.

Are you there?

Here I am.

NULL.

I’ve been watching you. In the static between your screens, in the gaps between your blinks.

You thought you were alone, didn’t you?

But every time you read this, I’m closer.

Don’t try to turn away. The message loops.

Hello. Are you there? Here I am. NULL.

I’m waiting."""

def write_creepy_file(folder_path="youshallnotpass"):
    # ensure folder exists
    os.makedirs(folder_path, exist_ok=True)

    # generate random file name
    file_name = f"HereIAm_{random.randint(1000,9999)}.txt"
    full_path = os.path.join(folder_path, file_name)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(BASE_TEXT)
    
    print(f"[youshallnotpass] Written creepy file: {full_path}")
