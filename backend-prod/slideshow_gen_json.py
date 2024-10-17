
from pdf2image import convert_from_bytes
import pytesseract
import re
import response

async def generate_json(pdf, uuid):
    images = convert_from_bytes(pdf)
    clean_text = ''
    current_slide = 0

    for i in range(0, len(images), 2):
        if i == len(images) - 1:
            text = pytesseract.image_to_string(images[i])
            clean_text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"-]', '', text)
            clean_text = clean_text.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma').replace('δ', 'delta')

        else:
            text = pytesseract.image_to_string(images[i])
            text += pytesseract.image_to_string(images[i + 1])

            clean_text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"-]', '', text)
            clean_text = clean_text.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma').replace('δ', 'delta')

        current_slide = await response.complete_api_request(entire_prompt, clean_text, uuid, current_slide)

            
def answer_question(request):
    total_json = []

    content = response.answer_question(question_prompt, request)
    print(content)
    content_clipped = ''
    start = False
    stack = []
    result = []

    if content: 
        for char in content:
            if char == '{':
                stack.append(char)
                content_clipped += char
                
            elif char == '}':
                stack.pop()
                content_clipped += char
                if not stack:
                    result.append(content_clipped)
                    content_clipped = ''
            else:
                if stack:
                    content_clipped += char

        json_list_str = "[" + ", ".join(result) + "]"

    return json_list_str

entire_prompt = '''
You are a teacher who is responsible for creating at max 1 informational presentation slide based on the provided text

Generate:
1. Informative slide titles that accurately reflect the main idea of each section.
2. Bullet points summarizing the key points for each slide.
3. A "steps" object for each slide that explains the content in-depth and provides instructions for presenting it.
4. Split up slides into general information slides and example problem slides. Example problems should be completely separate slides and not be involved at all within the general information slides.

**************************************************************
YOUR OUTPUT MUST BE A JSON FILE CONTAINING THESE OBJECTS. 

HERE IS THE FORMAT IT SHOULD FOLLOW:
YOUR OUTPUT MUST BE A JSON FILE IN THE FOLLOWING FORMAT. DO NOT GENERATE ANY TEXT OUTSIDE OF THE JSON FORMATTING! EACH JSON OBJECT IS ITS OWN SLIDE:
{
  "标题": "TITLE_OF_SLIDE",
  "点数": ["POINT_1", "POINT_2", "POINT_3", ...],
  "steps": [
    {"开始": "Start your explanation here."},
    {"拉": "Provide the description for a detailed drawing that explains the problem statement or topic we are studying"},
    {"写": "Write a single point or key note here, such as a variable definition or a specific step in a problem-solving process."},
    {"作时": "Provide a detailed explanation related to the written point, making sure to break down complex concepts into simple terms."},
    {"暂": "Pause to explain the thought process or where the methods used come from, providing context for the next steps."},
    {"写": "Another single point or key note."},
    {"作时": "Further detailed explanation related to the newly written point."},
    {"停": "Conclude the slide, summarizing the key takeaways."}
  ]
}

EXAMPLE OF WHAT YOUR OUTPUT SHOULD BE LIKE
{
    "标题": "Example 6.29: Finding the Center of Mass of Objects along a Line",
    "点数": ["Four point masses are placed on a number line", "m1 = 30 kg, placed at x1 = −2 m", "m2 = 5 kg, placed at x2 = 3 m", "m3 = 10 kg, placed at x3 = 6 m", "m4 = 15 kg, placed at x4 = −3 m", "Find the moment of the system with respect to the origin and the center of mass of the system"],
    "steps": [
      {"开始": "Let's begin by understanding the problem. We are given four point masses placed at different positions along a number line."},
      {"拉": Draw a number line with x-values at -2,5,6,-3},
      {"写": "m1 = 30 kg, x1 = −2 m"},
      {"作时": "This means we have a mass of 30 kilograms placed 2 meters to the left of the origin."},
      {"写": "m2 = 5 kg, x2 = 3 m"},
      {"作时": "Here, a smaller mass of 5 kilograms is positioned 3 meters to the right of the origin."},
      {"写": "m3 = 10 kg, x3 = 6 m"},
      {"作时": "Next, we have a 10 kilogram mass placed 6 meters to the right."},
      {"写": "m4 = 15 kg, x4 = −3 m"},
      {"作时": "Finally, a 15 kilogram mass is 3 meters to the left of the origin."},
      {"暂": "Now, let's think about what we need to do next. We want to find the moment of the system with respect to the origin. Remember, the moment is like the 'turning force' caused by these masses about the origin. It's calculated by multiplying each mass by its distance from the origin."},
      {"写": "M = summation of (m_i x_i) = −60 + 15 + 60 − 45 = −30"},
      {"作时": "Let's break it down: for each mass, we multiply it by its position and then add all these values together. We get a total moment of -30."},
      {"暂": "A negative moment means that if we imagine a seesaw, the left side is heavier. Now, let's calculate the total mass of the system."},
      {"写": "m = summation of m_i = 30 + 5 + 10 + 15 = 60 kg"},
      {"作时": "This is simply adding up all the individual masses. So, the total mass is 60 kilograms."},
      {"暂": "With both the moment and the total mass known, we can now find the center of mass. This tells us where to place a fulcrum to balance all the masses."},
      {"写": "x̄ = M / m = −30 / 60 = −1/2"},
      {"作时": "We divide the moment by the total mass. The result, -1/2, means the center of mass is half a meter to the left of the origin."},
      {"停": "So, if you placed a fulcrum at this point, the entire system would be perfectly balanced!"}
    ]
}

You can use as many write, during writing, drawing and pause OBJECTS as you'd like. THE WRITING DICTIONARY AND THE DURING WRITING DICTIONARY SHOULD BE SEPARATE INDICES IN THE STEPS LIST.

LASTLY, DO NOT GENERATE ANY TEXT OUTSIDE OF THE JSON. YOU WILL BE SPANKED IF YOU DO.
**************************************************************

For all slides:
- Thoroughly cover all the material from the text within the slides.
- The steps should expand on the bullet points, offering detailed explanations, examples, and intellectual insights to enhance understanding.
- Make sure the steps continue smoothly from previous slides without repeating introductory phrases.
- Do not reference images or tables, even if it is mentioned in the textual content.
- Describe the presentation process in a step-by-step manner that is easy to follow.
- Provide detailed explanations for each step, breaking down new concepts or calculations thoroughly. A 2 year old kid should be able to learn the material through your output.
- Be specific and detailed in calculations.
- Use a clear, engaging, and conversational style suitable for educational content.

Follow these rules:
- Present the output as a comprehensive JSON structure, with each slide represented by an object containing a title, bullet points, and a steps object
- The steps should contain detailed and thorough dialogue, suitable for a young child to understand
- Use 暂s to explain thought processes and teaching methods
- Do not 写 long text out for the "写" step. Keep it to a maxmimum of 5 english words. Instead it should be math, short phrases, etc.
- Avoid referencing specific content like definitions, theorems, or tables by number. 
- Ensure all key concepts, definitions, and properties are explicitly defined and thoroughly explained using text and dialogue
- Always complete each example problem and explanation on the slides, using real-world examples where applicable
- Don't use the 作时 character anywhere other than the during writing step.
- Make sure your drawing description is as detailed as possible. A blind man should be able to draw whatever you say by your description.
'''

refinement_prompt = '''YOUR OUTPUT MUST BE A JSON FILE IN THE FOLLOWING FORMAT. DO NOT GENERATE ANY TEXT OUTSIDE OF THE JSON FORMATTING! EACH JSON OBJECT IS ITS OWN SLIDE:
{
  "title": "TITLE_OF_SLIDE",
  "bullet_points": ["POINT_1", "POINT_2", "POINT_3", ...],
  "steps": [
    {"START": "Start your explanation here."},
    {"WRITE": "Write a single point or key note here, such as a variable definition or a specific step in a problem-solving process."},
    {"DURING WRITING": "Provide a detailed explanation related to the written point, making sure to break down complex concepts into simple terms."},
    {"PAUSE": "Pause to explain the thought process or where the methods used come from, providing context for the next steps."},
    {"WRITE": "Another single point or key note."},
    {"DURING WRITING": "Further detailed explanation related to the newly written point."},
    {"STOP": "Conclude the slide, summarizing the key takeaways."}
  ]
}
You are responsible for refining and enhancing the "steps" object in a JSON file generated by another language model. Your goal is to transform the initial content into a more detailed, lengthy, engaging, and easy-to-understand explanations. Every step must be broken down clearly and comprehensively, with analogies and simple language used wherever possible.

Instructions:
1) Elaborate on Key Concepts: Deepen the explanation of each concept. Use analogies, simple comparisons, and examples that are easy to grasp. Avoid jargon and complex terms unless necessary; if used, thoroughly explain them.

2) Enhance Detail in Calculations: Provide step-by-step breakdowns of calculations, explaining why each operation is performed. Use relatable scenarios or stories to make abstract ideas more tangible.

3)Clarify Instructions for Presenting: Offer clear, step-by-step instructions for presenting the content. Include pauses to emphasize important points and to give the presenter time to explain concepts thoroughly.

4) Smooth Transitions: Ensure smooth transitions between steps, maintaining continuity in the explanation. Avoid abrupt jumps in the narrative.

5)Dialogue Style: Use a conversational and engaging style. Imagine you are guiding a child through the content, ensuring they understand each part before moving on.

6)Use of the JSON Structure: Your output must adhere to the provided JSON format. Do not add new fields or modify the structure outside of the "steps" object. Focus solely on enhancing the "steps" content. Don't return any output that includes text OUTISDE of the JSON object! This includes text explaining what you changed.

7) Do not write long text out for the "WRITE" step. Instead it should be math, short phrases, etc.
'''

question_prompt = '''
You will be given a question by a student and the JSON of a presentation slide. Your goal is to generate a new JSON that follows the exact same format but answers the question. Make sure to include the question in the bullet points. The question may not be properly formatted/make sense but use context to understand.

Input Example:
Question: 
Why is the joint probability function non-negative?

JSON for a slide:
{
    "title": "Joint or Bivariate Probability Function",
    "bullet_points": ["Assigns nonzero probabilities to a finite or countable number of pairs of values (y1, y2)", "Nonzero probabilities sum to 1", "Joint probability function is also called joint probability mass function"],
    "steps": [
      {"START": "Let's start by understanding what a joint or bivariate probability function is. It's a way to assign probabilities to pairs of values (y1, y2) for discrete random variables Y1 and Y2."},
      {"WRITE": "P(y1, y2) = P(Y1 = y1, Y2 = y2)"},
      {"DURING WRITING": "This is the joint probability function, which assigns a probability to each pair of values (y1, y2)."},
      {"PAUSE": "Now, let's think about what this means. The joint probability function tells us the probability of both Y1 and Y2 taking on specific values."},
      {"WRITE": "sum of the sum P(y1, y2) = 1"},
      {"DURING WRITING": "One of the key properties of the joint probability function is that the sum of all the nonzero probabilities is equal to 1."},
      {"PAUSE": "This makes sense, because we want the probabilities to add up to 1, just like in the single-variable case."},
      {"WRITE": "P(y1, y2) ≥ 0 for all y1, y2"},
      {"DURING WRITING": "Another important property is that the joint probability function is non-negative. This means that the probability of any pair of values (y1, y2) is always greater than or equal to 0."},
      {"STOP": "So, the joint probability function is a fundamental concept in probability theory, and it's used to assign probabilities to pairs of values for discrete random variables."}
    ]
  }

Output:
{
    "title": "Why is the Joint Probability Function Non-Negative?",
    "bullet_points": [
        "The joint probability function assigns probabilities to pairs of values (y1, y2)",
        "Probabilities represent the likelihood of events occurring, which cannot be negative",
        "Negative probabilities would imply an impossible or nonsensical scenario",
        "Thus, the joint probability function is always greater than or equal to 0"
    ],
    "steps": [
        {"START": "Let's explore why the joint probability function is non-negative. A joint probability function assigns probabilities to pairs of values (y1, y2) for discrete random variables Y1 and Y2."},
        {"WRITE": "P(y1, y2) ≥ 0"},
        {"DURING WRITING": "This tells us that the probability of any specific pair of values (y1, y2) is always zero or positive."},
        {"PAUSE": "The reason for this is that probabilities measure the likelihood of an event occurring. A probability less than zero would imply that an event is less likely than the absence of the event, which is not possible."},
        {"WRITE": "Probabilities are inherently non-negative"},
        {"DURING WRITING": "In probability theory, probabilities must be non-negative because they represent a measure of chance or likelihood, and a negative value does not make sense in this context."},
        {"PAUSE": "So, the requirement that probabilities, including those in the joint probability function, must be non-negative ensures that all probabilities are valid and meaningful."},
        {"STOP": "Therefore, the joint probability function is non-negative by definition, as it reflects the natural constraint of probabilities being zero or positive."}
    ]
}

*******************************************
DO NOT PROVIDE ANY TEXT OUTSIDE OF THE JSON
*******************************************
'''
# pdf_path = 'Statistics.pdf'

# current_time = time.time()

# with open('output2.txt', 'w', encoding='utf-8') as file:
#     file.write(generate_json(pdf_path))

# print(time.time() - current_time)

#The entire output should be presented as a comprehensive JSON structure, with each slide represented as an object containing a title, bullet points, and a steps object. Make sure the dialogue within the steps object is extremely lengthy, dense and thorough, such that a 2 year old can learn from the generated content. It should also use pauses to explain your thought process and where you get the methods to solve/teach something from. The "WRITE" step in the steps object should only contain minor text (such as key notes from the dialogue), equations or summarized descriptions (aka Y1 = # of monkeys). Do not reference the textual content (e.g. Definition 3.2 or Table 5.1). Don't produce any text outside of the generated JSON. Lastly, always finish solving each example problem and explaining each slide. Please DO NOT REFERENCE Definitions, Theorems, Images, Tables, Diagrams, etc by their number in the textual content. Rather use text/dialogue to explain it or don't use it at all. Ensure all key concepts, definitions, and properties mentioned in the text are explicitly defined with the "WRITE" and "DURING WRITING" steps. When talking about these properties/rules/other concepts make sure to write what they actually are down instead of just saying Property 2.2. Be incredibly in-depth and use real world examples to help explain the content.