import streamlit as st
#from langchain import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import ChatPromptTemplate
#from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
import requests

st.set_page_config(
    page_title="Recipe App",
    page_icon="🍳",
    initial_sidebar_state="expanded",
)
st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):
    user_input = prompt.split(",")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(user_input)


    API_KEY = ''

    base_url = 'https://api.spoonacular.com/recipes/findByIngredients'
    ingredients = user_input
    params = {
        'ingredients': ','.join(ingredients),
        'apiKey': API_KEY,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        recipes = response.json()
        for recipe in recipes:  
            recipe_id = recipe['id']
            recipe_title = recipe['title']

            instructions_url = f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions'
            instructions_params = {
                'apiKey': API_KEY
            }
            instructions_response = requests.get(instructions_url, params=instructions_params)
            
            if instructions_response.status_code == 200:
                instructions_data = instructions_response.json()
                if instructions_data:
                    steps = []
                    all_recipes = [] 
                    for instruction in instructions_data[0]['steps']:
                        steps.append(instruction['step'])
                    # Printing recipe details
                    #st.write(f"Recipe ID: {recipe_id}")
                    st.header(f"Recipe Title: {recipe_title}")
                    used_ingredients = recipe['usedIngredients']
                    st.write("Used Ingredients:")
                    for ingredient in used_ingredients:
                        st.write(f"- {ingredient['name']} - Amount: {ingredient['amount']} {ingredient['unit']}")
                        missed_ingredients = recipe['missedIngredients']
                    st.write("Missed Ingredients:")
                    for ingredient in missed_ingredients:
                        st.write(f"- {ingredient['name']} - Amount: {ingredient['amount']} {ingredient['unit']}")

                    st.write("Instructions:")
                    for step in steps:
                        st.write(f"- {step}")

                    recipe_details = {
                        #"Recipe ID": recipe_id,
                        "Recipe Title": recipe_title,
                        "Used Ingredients": used_ingredients,
                        "Missed Ingredients": missed_ingredients,
                        "Instructions": steps
                    }
                    all_recipes.append(recipe_details)
                    st.write("\n" + "-"*30 + "\n")
                else:
                    st.write(f"No instructions available for recipe '{recipe_title}'.")
            else:
                st.write(f"Error fetching instructions for recipe '{recipe_title}': {instructions_response.status_code}")
    else:
        st.write(f"Error: {response.status_code} - {response.text}")



if prompt := st.chat_input("Ask your question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    get_input_question = prompt

    template = """
        your goal is to answer users questions about recipes.
        
        Below is userInput:
        questions: {questions}
        all_recipies: {all_recipes}
        
        YOUR RESPONSE:

    """

    prompt = PromptTemplate(
    input_variables=["questions", "all_recipes"],
    template=template,
    )

    def load_LLM():
        llm = OpenAI(temperature=0.9, openai_api_key="")
        #llm = OpenAI(temperature=0.9)
        return llm

    llm = load_LLM()

    if get_input_question:
        prompt_our_dishes = prompt.format(all_recipes=all_recipes, questions=get_input_question)
        Answer = llm(prompt_our_dishes)
        st.write(Answer)
        with st.chat_message("assistant"):
            response = st.write_stream(Answer)
        st.session_state.messages.append({"role": "assistant", "content": Answer})