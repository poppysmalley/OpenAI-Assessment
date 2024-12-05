# Comic Strip Generator using OpenAI


I made a comic strip generator using OpenAI's GPT-4o and DALL·E 3. It takes a short story and generates a series of captioned images to create a comic strip.

It works by using GPT-4o to separate the story into descriptions for each panel, alongside a more general description of the style, setting, and characters. This general description is then provided alongside the individual panel descriptions in turn as a prompt to DALL·E 3 to generate images. It is important to include the general description to maintain consistency between images. The images are then combined with the captions and the final image is saved.


## Example Story and Image Results

Here is an example short story that was used to generate a comic strip:

> In a dense jungle, far from the eyes of civilization, a brave explorer named Max sets out on an adventure to discover the fabled Hidden Temple. Armed with only a map and his courage, Max navigates the perilous terrain, crossing rivers and climbing steep hills.
After days of traveling, Max stumbles upon an ancient, overgrown entrance covered in vines. He pushes through the thick foliage, revealing the mysterious temple. It’s made of stone, with intricate carvings of forgotten gods.
Max carefully enters the temple and discovers a large chamber. In the center of the room lies a glowing artifact. As he approaches it, he feels the weight of history and destiny upon him. With one final look at the artifact, Max grabs it, and the temple begins to shake.
He races out just as the temple collapses behind him, narrowly escaping with the artifact in hand. Max returns to the village as a hero, the artifact now in his possession, its secrets ready to be unlocked.

This is the image that was produced:

![Comic Strip](comic_strip.png)  
