import openai

from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")

problem = 'Let $\triangle ABC$ have circumcenter $O$ and incenter $I$ with $\overline{IA}\perp\overline{OI}$, circumradius $13$, and inradius $6$. Find $AB\cdot AC$.'
steps = []

tutor = 'Your job is to provide the consequent step in solving the math problem, given the current list of steps. Make sure to calculate each step and use LaTeX for special characters. When the problem is solved, respond with "DONE". Use < 3 sentences or < 2 math expressions per step. Do not tell me what the step after the next step should be.'

critic = f'''
For this conversation, you will mention if there is something wrong with the math problem solver's latest step in the list in how to solve the given math problem. If they're right, tell them they're on the right track. If they're wrong, give them feedback on what to improve in their step but do not show the next step. They can be wrong mathematically or conceptually, so tell them what to fix. This should not be subjective feedback, only objective.
'''

modifier = f'''
For this conversation, you will take in the input from a critic who criticized the math problem solver's latest step in the given list for solving the problem. With this criticism, you will provide a new step that should replace the latest one in the list. Please only provide the new step with no external text. Please provide the step in a way such that you solve it out yourself, instead of telling me what to do.
'''

def complete_api_request(prompt, text):
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        max_tokens = 1024,
        stream=True,
        temperature=1,
        top_p=1,
        frequency_penalty = 0,
        presence_penalty = 0,
    )

    content = ''

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content

    return content

def solve_problem():
    user_prompt = f'''
        Problem:
        {problem}

        Steps:
        {steps}
    '''
    while True:
        print('--------------------------------------------------')
        tutor_response = complete_api_request(tutor, user_prompt)
        print ('Tutor:', tutor_response)
        
        if 'DONE' in tutor_response:
            break

        steps.append(tutor_response)
        user_prompt = f'''
            Problem:
            {problem}

            Steps:
            {steps}
        '''

        critic_response = complete_api_request(critic, user_prompt)
        critic_prompt = f'''
        Criticism:
        {critic_response}

        {user_prompt}
        '''

        print ('Critic:', critic_response)

        modifier_response = complete_api_request(modifier, critic_prompt)
        steps[-1] = modifier_response

        print('Modified', modifier_response)
        print('--------------------------------------------------', '\n')
    return steps

print(solve_problem())