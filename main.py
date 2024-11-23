import random
import json
from fuzzywuzzy import fuzz
from pywebio import start_server, config
from pywebio.input import input, TEXT, checkbox
from pywebio.output import put_row, put_button, put_markdown, clear, put_text, put_html


def load_recipes(filename='train.json'):
    # Loads recipes from the JSON file #
    try:
        with open(filename, 'r') as file:
            recipes = json.load(file)
        print("Recipes loaded successfully:", len(recipes))  # Debug: Print the number of recipes loaded #
        return recipes
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading recipes: {e}")
        return []  # Return an empty list if there's an error #


def find_matching_recipes(recipes, input_ingredients, cuisine=None):
    # Finds recipes that have matching ingredients #
    matching_recipes = []
    for recipe in recipes:
        recipe_ingredients = recipe.get("ingredients", [])
        if cuisine and recipe.get('cuisine', '').lower() != cuisine.lower():
            continue

        # Fuzzy matching for each ingredient #
        for input_ingredient in input_ingredients:
            if any(fuzz.partial_ratio(input_ingredient.lower(), ing.lower()) >= 95 for ing in recipe_ingredients):
                # Uses fuzz to find close ingredients #
                matching_recipes.append(recipe)
                break  # Move on to the next recipe once a match is found #

    return matching_recipes


def filter_by_allergies(recipes, allergies_input):
    # Filters recipes based on comma-separated list of allergies #
    if not allergies_input:
        return recipes
    allergy_set = set(allergies_input.lower().split(","))
    return [
        recipe
        for recipe in recipes
        if not allergy_set.intersection(ing.lower() for ing in recipe.get("ingredients", []))
    ]


# Main homepage #
@config(title="JRF - Homepage")
def homepage():

    put_html("<h2>Jack's Recipe Finder</h2>")  # Heading inside the container

    put_row([  # Button row also inside the container
        put_button('Recipe Finder!', onclick=lambda: navigate('page1'), color='success'),
        put_button('Random Recipe', onclick=lambda: navigate('page2')),
        put_button('Cupboard Staples', onclick=lambda: navigate('page3'), color='warning')
    ])


# Page 1: Recipe Finder #
def page1():
    recipes = load_recipes('train.json')

    put_markdown("# Recipe Finder")

    # Cuisine selection via checkbox #
    cuisines = sorted({recipe.get('cuisine', '').capitalize() for recipe in recipes})
    selected_cuisines = checkbox("Select cuisines:", options=cuisines)

    user_input = input("Enter ingredients separated by commas:", type=TEXT)
    input_ingredients = [ing.strip().lower() for ing in user_input.split(',')]
    set(input_ingredients)

    allergies = input("Enter your allergies separated by commas, if none - leave blank:", type=TEXT)

    filtered_recipes = []
    for cuisine in selected_cuisines:
        # Filter by cuisine and ingredients #
        matching_recipes = find_matching_recipes(recipes, input_ingredients, cuisine)

        # Filter by allergies #
        filtered_for_cuisine = filter_by_allergies(matching_recipes, allergies)
        print(filtered_for_cuisine)
        if filtered_for_cuisine:
            # Choose one recipe from the filtered list for this cuisine #
            chosen_recipe = random.choice(filtered_for_cuisine)
            filtered_recipes.append(chosen_recipe)

    if filtered_recipes:
        # Display the selected recipes
        put_markdown("## Your matching recipe:")
        for recipe in filtered_recipes:
            put_markdown(f"- **{recipe.get('id', 'Unknown ID')}:** {recipe.get('cuisine', 'Unknown cuisine')}")
            put_text("Ingredients:")
            for ingredient in recipe.get('ingredients', []):
                put_text(f"  - {ingredient}")
            put_html("<br>")  # Add spacing between recipes #

    else:
        put_text("Very sorry, No recipes found!")
        put_text("Make sure you're selecting a cuisine.")
        put_text("Try simplifying your inputs.")

    put_button("Back", onclick=lambda: navigate('homepage'))


# Page 2: Random Recipe #
def page2():
    recipes = load_recipes('train.json')

    if recipes:
        # Choose a random recipe
        chosen_recipe = random.choice(recipes)

        # Display the selected recipe
        put_text("Here's a random recipe:")
        put_markdown(
            f"- **{chosen_recipe.get('id', 'Unknown ID')}:** {chosen_recipe.get('cuisine', 'Unknown cuisine')}")
        put_text("Ingredients:")
        for ingredient in chosen_recipe.get('ingredients', []):
            put_text(f"  - {ingredient}")
    else:
        put_text("No recipes found in the database.")

    put_button("Back", onclick=lambda: navigate('homepage'))


def page3():
    put_markdown("# Cupboard Staples")
    # List of top 10 most common ingredients from dataset #
    cupboard_staples = ["salt", "onions", "olive oil", "water", "garlic", "sugar", "garlic cloves", "butter",
                        "ground black pepper", "all-purpose flour"]
    selected_staples = checkbox("Select your cupboard staples:", options=cupboard_staples)
    if selected_staples:
        navigate('page1')
    else:
        put_text("Please select at least one staple.")
    put_button("Back", onclick=lambda: navigate('homepage'))


# Function to navigate between pages #
def navigate(page_name):
    clear()
    if page_name == 'homepage':
        homepage()
    elif page_name == 'page1':
        page1()
    elif page_name == 'page2':
        page2()
    elif page_name == 'page3':
        page3()


# Start the server
if __name__ == '__main__':
    start_server(homepage, port=8081, debug=True)
