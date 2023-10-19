#from dotenv import load_dotenv
import os
import random
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain, SequentialChain


def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="→ 🤖 → 🕸️ IdeaVault!",
        page_icon="💡",
        layout="centered"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

#load_dotenv()
#API_KEY = os.environ['OPENAI_API_KEY']

customize_streamlit_ui()

API_KEY = st.secrets["OPENAI_API_KEY"]

llm = OpenAI(openai_api_key=API_KEY, temperature=0.9)

ingredients_template = """
I want you to act as a recipe database. Using the following ingredients: {ingredients}, generate an authentic recipe that can be made with these items. Please provide the recipe exactly, with measurements in metric units -- that means no mention of onces, pounds or inches. Very important: You cannot include ingredients that have not been provided.
"""
prompt_template = PromptTemplate(
    template=ingredients_template,
    input_variables=['ingredients']
)

gangster_template = """
I want you to act as an Italian mafia boss with a serious passion for cooking. Rewrite the recipe I'm going to provide, using the nuanced tone and vernacular of an old-school mafia boss. While adding character and flair, avoid making it too cartoony. The aim is to maintain the authenticity of the persona while ensuring the recipe is still clear and easy to follow.

Meal:
{meals}
"""

gangster_template_prompt = PromptTemplate(
    template=gangster_template,
    input_variables = ['meals']
)

meal_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    output_key="meals",
    verbose=True
)

gangster_chain = LLMChain(
    llm=llm,
    prompt=gangster_template_prompt,
    output_key="gangster_meals",
    verbose=True
)

overall_chain = SequentialChain(
    chains=[meal_chain, gangster_chain],
    input_variables=['ingredients'],
    output_variables=["meals", "gangster_meals"],
    verbose=True
)

american_to_british = {
    "skillet": "frying pan",
    "zucchini": "courgette",
    "eggplant": "aubergine",
    "cilantro": "coriander",
    "cookie": "biscuit",
    "chips": "crisps",
    "fries": "chips",
    # ... add more as needed
}

our_family = ["Ellen", "Lerey", "Renate", "Mama V", "Kim", "The IT Boys"]

def get_random_name():
    return random.choice(our_family)

def personalize_recipe_name(recipe_name):
    # Get a random name
    name = get_random_name()
    # Personalize the recipe name
    personalized_name = f"{name}'s:\n\n{recipe_name}"
    return personalized_name


st.title("Our Home Meal Planner")
user_prompt = st.text_input("Enter a list of ingredients")

def american_to_british_translation(text):
    for american, british in american_to_british.items():
        text = text.replace(american, british)
    return text

if st.button("Generate") and user_prompt:
    with st.spinner("Generating..."):
        output = overall_chain({'ingredients': user_prompt})

        # Translate American English to British English
        output['meals'] = american_to_british_translation(output['meals'])
        output['gangster_meals'] = american_to_british_translation(output['gangster_meals'])

        # Personalize the recipe names (assuming 'meals' contains the recipe name)
        output['meals'] = personalize_recipe_name(output['meals'])
        output['gangster_meals'] = personalize_recipe_name(output['gangster_meals'])

        col1, col2 = st.columns(2)
        col1.write(output['meals'])
        col2.write(output['gangster_meals'])
