from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bs4 import BeautifulSoup
import logging
import json
import requests

# Secret Keys
api_key = '95f55c93efc94e37af288be74236e55f'
telegram_token = '1375488285:AAFkFZ73M2pJUhbv0DRExg0I1Gk27ncaXaw'

updater = Updater(token=telegram_token, use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    text = text.replace('. ', '.\n')
    text = text.replace('.', '.\n')
    print(text)
    return text


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


def start(update, context):
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo="https://media.gettyimages.com/photos/young-man-at"
                                 "-sunset-picture-id496261146?s=2048x2048",
                           caption="I'm a *bot*, please talk to me\!", parse_mode="MarkdownV2")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def get_random_recipe():
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={api_key}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


def get_veg_recipe():
    response = requests.get(
        f"https://api.spoonacular.com/recipes/random?number=1&tags=vegetarian&apiKey={api_key}").text
    response = json.loads(response)
    recipe_info = create_output(response)
    return recipe_info


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
