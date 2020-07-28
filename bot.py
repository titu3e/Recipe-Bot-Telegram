import config
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import logging
import json
import requests

# Initialize the Updater to listen for commands/messages received
updater = Updater(token=config.telegram_token, use_context=True)
dispatcher = updater.dispatcher

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


# Extract data from api request's response
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


# Function for start command
def start(update, context):
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo="https://i.pinimg.com/236x/78/a1/97/78a19719c209a8e4cad29e6f7ee1e2a5--minimal.jpg",
                           caption="*Do you want a recipe today\?*\n*Commands:*\n1\.random \- Gives you a random "
                                   "recipe\n2\.veg \- Gives you random veg recipe\n3\.nonveg \- Gives you random "
                                   "non\-veg recipe", parse_mode="MarkdownV2")


# Create handler for start command
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def get_random_recipe():
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={config.api_key}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


def get_veg_recipe():
    response = requests.get(
        f"https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian&apiKey={config.api_key}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


def get_nonveg_recipe():
    response = requests.get(
        f"https://api.spoonacular.com/recipes/random?number=1&tags=primal&apiKey={config.api_key}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


def nonveg(update, context):
    recipe = get_nonveg_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


nonveg_handler = CommandHandler('nonveg', nonveg)
dispatcher.add_handler(nonveg_handler)


def veg(update, context):
    recipe = get_veg_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


veg_handler = CommandHandler('veg', veg)
dispatcher.add_handler(veg_handler)


def random(update, context):
    recipe = get_random_recipe()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=recipe[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=recipe[0], parse_mode='HTML')


random_handler = CommandHandler('random', random)
dispatcher.add_handler(random_handler)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

# Start the bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT
updater.idle()
