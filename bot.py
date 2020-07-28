"""
Simple bot that replies to telegram commands with yummy recipes!
Deployed using Heroku

Author: tanmayc07
"""

import os
# import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import logging
import json
import requests

PORT = int(os.environ.get('PORT', 5000))

# Log any exceptions or errors with timestamp
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# Function to parse html returned from api request
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    text = text.replace('. ', '.\n')
    text = text.replace('.', '.\n')
    return text


# Function to extract data from api request's response
def create_output(response):
    recipe_title = response['recipes'][0]['title']
    recipe_time = response['recipes'][0]['readyInMinutes']
    recipe_img = response['recipes'][0]['image']
    recipe_instructions = parse_html(response['recipes'][0]['instructions'])
    recipe_ingredients = ""
    for ingredient in response['recipes'][0]['extendedIngredients']:
        recipe_ingredients += ingredient['name'] + "\n"
    recipe_info = [recipe_title, recipe_time, recipe_img, recipe_instructions]
    message = f"<b>Title</b>: <pre>{recipe_info[0]}</pre>\n\nIt will take you <b>{recipe_info[1]}mins</b> to " \
              f"cook!\n\n<b>Ingredients</b>:\n<pre>{recipe_ingredients}</pre>\n\n<b>Instructions📃</b>:\n<pre>{recipe_info[3]}</pre> "
    photo = recipe_info[2]
    return [message, photo]


# Function to fetch random recipe from api
def get_random_recipe():
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={os.environ.get('API_KEY')}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


# Function to fetch random veg recipe from api
def get_veg_recipe():
    response = requests.get(
        f"https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian&apiKey={os.environ.get('API_KEY')}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


# Function to fetch random non-veg recipe from api
def get_nonveg_recipe():
    response = requests.get(
        f"https://api.spoonacular.com/recipes/random?number=1&tags=primal&apiKey={os.environ.get('API_KEY')}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


# Function for start command
def start(update, context):
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo="https://i.pinimg.com/236x/78/a1/97/78a19719c209a8e4cad29e6f7ee1e2a5--minimal.jpg",
                           caption="*Do you want a yummy recipe today\?*\n*Commands:*\n1\.random \- Gives you a random "
                                   "recipe\n2\.veg \- Gives you random veg recipe\n3\.nonveg \- Gives you random "
                                   "non\-veg recipe", parse_mode="MarkdownV2")


def nonveg(update, context):
    """Send a non-veg recipe as message when the command /nonveg is issued."""
    recipe = get_nonveg_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


def veg(update, context):
    """Send a veg recipe as message when the command /veg is issued."""
    recipe = get_veg_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


def random(update, context):
    """Send a random recipe as message when the command /veg is issued."""
    recipe = get_random_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


def echo(update, context):
    """Echo the user message."""
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def unknown(update, context):
    """Send a reply if unknown command is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I can only send you yummy recipes.")


def main():
    """Start the bot"""
    # Initialize the Updater to listen for commands/messages received
    updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # Create handler for start command
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    veg_handler = CommandHandler('veg', veg)
    dispatcher.add_handler(veg_handler)

    nonveg_handler = CommandHandler('nonveg', nonveg)
    dispatcher.add_handler(nonveg_handler)

    random_handler = CommandHandler('random', random)
    dispatcher.add_handler(random_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # Start the bot
    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=os.environ.get('TELEGRAM_TOKEN'))
    updater.bot.setWebhook('https://glacial-waters-08425.herokuapp.com/' + os.environ.get('TELEGRAM_TOKEN'))

    # Run the bot until you press Ctrl-C or the process receives SIGINT
    updater.idle()


if __name__ == "__main__":
    main()
