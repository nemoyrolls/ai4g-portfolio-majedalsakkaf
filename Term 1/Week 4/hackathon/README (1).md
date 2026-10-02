
# Will They Build One Too?

A short Christmas climate film created for Hackathon 4: Picture the Planet.

## Tool and SDG

- **Required tool:** ComfyUI
- **SDG:** SDG 13: Climate Action

## The problem and audience

Warmer winters mean fewer opportunities for children to build snowmen. Our film makes this change personal by showing how it could affect a family tradition.

Our primary audience is young people aged 16–25 in the Netherlands. The film encourages them to discuss climate change with their families. It is not primarily intended for young children or viewers seeking a detailed scientific explanation.

## Our film

The story follows a family’s snowman tradition across two generations. A child and parent build a snowman, but the snowmen become smaller as time passes. In a fictional future set in 2045, the original child returns as a parent. Their child holds a carrot, but there is no snowman to put it in.

The red scarf connects the generations, while the same backyard connects the scenes.

**Message:** “The climate we leave becomes their childhood.”

**Call to action:** “This Christmas, talk about it. Choose one change together.”

The film supports SDG 13 by raising awareness of climate change and encouraging practical family action.

## Watch the film

- **YouTube:** https://youtu.be/mAOLVUL8Pac?is=7xlkZZBgcpm57DBZ
  
## How we created it

1. **Z-Image Turbo:** generated the still images in ComfyUI.
2. **MiniMax H3 i2V:** turned the images into video clips.
3. **ElevenLabs:** generated the narration.
4. **Claude Code:** helped edit and combine the clips into the final film.

**Final output:** a 53-second horizontal film and the ComfyUI workflow file.

## How to run it

To watch the film, open the YouTube link.

To recreate it:
1. Open ComfyUI and load our exported workflow JSON.
2. Install the required models and nodes, then generate the images using the saved prompts and settings.
3. Generate the video clips with MiniMax H3 i2V and the narration with ElevenLabs.
4. Use the editing scripts and instructions from our project to assemble the final film.

The ComfyUI workflow alone does not recreate the complete film.

**Workflow file:** [Add the workflow JSON link]

**Required models and custom nodes:** 
The project uses the standard ComfyUI template workflows with the following models:

- Z-Image Turbo — Text-to-Image generation
- MiniMax H3 — Image-to-Video generation
- Qwen 2.1 — Text/Image-Edit-Image workflow

No additional custom nodes were used beyond those required by the standard ComfyUI template workflows.
## Who did what?

Majed al-Sakkaf and I brainstormed the concept together. Majed handled the main technical production, including the ComfyUI workflow and generating the film’s visuals. I wrote the storyboard and created the presentation.

We both contributed throughout the making of the film and gave each other feedback to improve the final result.

## Ethical reflection

Viewers could mistake our generated scenes for real footage or interpret 2045 as a scientific prediction. The story therefore needs a clear label explaining that it is AI-generated fiction and that the future scene is illustrative. Our characters are AI-generated, and we avoid intentionally using real people’s likenesses. The message encourages achievable family choices without blaming viewers or making them feel solely responsible for climate change.


## Climate source

KNMI explains that warming reduces the number of days cold enough for snow in the Netherlands. Our fictional story illustrates this broader trend; it does not document specific historical winters or predict the weather in 2045.

[KNMI: Sneeuw in Nederland steeds zeldzamer](https://www.knmi.nl/over-het-knmi/nieuws/sneeuw-in-nederland-steeds-zeldzamer)

## Project files

- Final film- https://youtu.be/mAOLVUL8Pac?is=7xlkZZBgcpm57DBZ
- ComfyUI workflow JSON
- Storyboard and shot list- https://app.milanote.com/1XaakZ1y0AsS91?p=x5kVnrXH7Bl
- Presentation- https://canva.link/3tjvy1kf7nfe0kx


  
