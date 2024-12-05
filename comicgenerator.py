from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

client = OpenAI()


# Function to break down the short story into prompts for panels in a comic strip
def generate_comic_script(story):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
                    "You are a helpful assistant that transforms short stories into comic strip breakdowns. "
                    "Provide the response in the following format:\n\n"
                    "Description: A detailed description combining the art style, setting, and characters for consistency.\n"
                    "Panels:\n"
                    "Panel Description 1: <Description of the scene for the image generation>\n"
                    "Caption 1: <Caption to appear below the panel>\n"
                    "Panel Description 2: <Description of the scene for the image generation>\n"
                    "Caption 2: <Caption to appear below the panel>\n"
                    "... (continue for all panels)")},
            {"role": "user", "content": f"Convert the following short story into a comic strip breakdown. Ensure the descriptions are detailed for consistent image generation, such as including clothing colours for characters. In the panel descriptions, say which characters are present in the image and which characters are not. Do not use quotation marks for the captions and do not make each caption longer than 100 characters. Here is the story: {story}"}
        ]
    )
    return response.choices[0].message.content


# Function to separate the response into individual prompts and captions for each panel
def parse_comic_script(script):
    lines = script.split("\n")
    description = ""
    panels = []
    current_panel = None

    for line in lines:
        line = line.strip()
        if line.startswith("Description:"):
            description = line[len("Description:"):].strip()
        elif line.startswith("Panels:"):
            continue
        elif line.startswith("Panel Description"):
            if current_panel:
                panels.append(current_panel)
            current_panel = {"Description": line[len("Panel Description  :"):].strip(), "Caption": ""}
        elif line.startswith("Caption"):
            if current_panel:
                current_panel["Caption"] = line[len("Caption  :"):].strip()
    if current_panel:
        panels.append(current_panel)

    return {"Description": description, "Panels": panels}


# Function to generate comic strip images based on the panel descriptions
def generate_comic_images(description, panels):
    
    comic_images = []
    for panel in panels:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"{description} Do not include text in the image. The image shows: {panel['Description']}",
            n=1,
            size="1024x1024"
        )
        comic_images.append({
        "Image": response.data[0].url,
        "Caption": panel["Caption"]})
    return comic_images


# Function to combine the images and their captions into a comic strip
def create_comic_strip(image_data, panel_size=(1024, 1024), panels_per_row=3, border_size=20):
   
    # Load images and resize to uniform panel size
    panels = []
    for data in image_data:
        url = data["Image"]
        caption = data["Caption"]
        
        # Get image from URL
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize(panel_size)

        # Add a white border around each image, with space for captions
        bordered_panel = Image.new("RGBA", (panel_size[0] + 2 * border_size, panel_size[1] + 2 * border_size + 80), "white")
        bordered_panel.paste(img, (border_size, border_size))
        
        # Add caption under the panel
        draw = ImageDraw.Draw(bordered_panel)
        font = ImageFont.truetype("arial.ttf", 40)

        # Calculate text size using textbbox
        caption_bbox = draw.textbbox((0, 0), caption, font=font)
        caption_height = caption_bbox[3] - caption_bbox[1]

        # Split caption into multiple lines if it is too wide for the panel
        max_line_length = panel_size[0] - 2 * border_size
        words = caption.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Check if the word fits in the current line
            if draw.textbbox((0, 0), current_line + " " + word, font=font)[2] - caption_bbox[0] <= max_line_length:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:  # Add the last line
            lines.append(current_line)

        # Draw the caption lines under the image
        caption_y = panel_size[1] + border_size
        for line in lines:
            caption_bbox = draw.textbbox((0, caption_y), line, font=font)
            caption_width = caption_bbox[2] - caption_bbox[0]
            caption_x = (bordered_panel.width - caption_width) // 2
            draw.text((caption_x, caption_y), line, fill="black", font=font)
            caption_y += caption_height

        panels.append(bordered_panel)

    # Calculate dimensions for the final comic strip
    num_panels = len(panels)
    num_rows = (num_panels + panels_per_row - 1) // panels_per_row
    panel_width_with_border = panel_size[0] + 2 * border_size
    panel_height_with_border = panel_size[1] + 2 * border_size + 80
    strip_width = panel_width_with_border * panels_per_row
    strip_height = panel_height_with_border * num_rows

    # Create a blank canvas for the comic strip
    comic_strip = Image.new("RGBA", (strip_width, strip_height), (255, 255, 255, 255))

    # Paste each panel onto the canvas
    for i, panel in enumerate(panels):
        x = (i % panels_per_row) * panel_width_with_border
        y = (i // panels_per_row) * panel_height_with_border
        comic_strip.paste(panel, (x, y))

    return comic_strip



# Short story input
short_story = """In a dense jungle, far from the eyes of civilization, a brave explorer named Max sets out on an adventure to discover the fabled Hidden Temple. Armed with only a map and his courage, Max navigates the perilous terrain, crossing rivers and climbing steep hills.
After days of traveling, Max stumbles upon an ancient, overgrown entrance covered in vines. He pushes through the thick foliage, revealing the mysterious temple. It’s made of stone, with intricate carvings of forgotten gods.
Max carefully enters the temple and discovers a large chamber. In the center of the room lies a glowing artifact. As he approaches it, he feels the weight of history and destiny upon him. With one final look at the artifact, Max grabs it, and the temple begins to shake.
He races out just as the temple collapses behind him, narrowly escaping with the artifact in hand. Max returns to the village as a hero, the artifact now in his possession, its secrets ready to be unlocked."""



# Generate comic strip

comic_script = generate_comic_script(short_story)
print("Comic Script:\n", comic_script)

parsed_script = parse_comic_script(comic_script)
description = parsed_script["Description"]
panels = parsed_script["Panels"]

comic_images = generate_comic_images(description, panels)
final_comic = create_comic_strip(comic_images)

final_comic.save("comic_strip.png")
final_comic.show()
