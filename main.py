import os
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.types import Message
from teliqon_billing import BillingAPI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
BILLING_API_KEY = os.getenv('BILLING_API_KEY')
BILLING_ENV = int(os.getenv('BILLING_ENV'))


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)
billing_api = BillingAPI(api_token=BILLING_API_KEY, environment_id=BILLING_ENV)


@dp.message_handler(commands='start')
async def start(message: Message):
    billing_api.create_user(
        unique_id=str(message.from_user.id), 
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        credit_limit=-1000
    )

    await message.answer("Wellcome!")


@dp.message_handler(commands='pay')
async def pay(message: Message):
    amount = float(message.get_args())
    users = billing_api.get_users()
    
    amount_to_user = amount / len(users)

    for user in users:
        if user.unique_id == str(message.from_user.id):
            continue

        transaction = billing_api.in_system_transfer(user.unique_id, str(message.from_user.id), amount_to_user, comment='-')
        try:
            trns = f'''ID: {transaction.id}
Amount: {transaction.amount}'''
            await bot.send_message(
                chat_id=int(user.unique_id),
                text=trns
            )
        except:
            pass

    await message.answer("Payed")


@dp.message_handler(commands='who')
async def who(message: Message):
    users = billing_api.get_users()
    user = users[0]

    for u in users:
        if u.balance < user.balance:
            user = u
    
    await message.answer(f"{user.first_name} {user.last_name}")


@dp.message_handler(commands='balance')
async def balance(message: Message):
    u = billing_api.get_user(unique_id=str(message.from_user.id))
    await message.answer(f"{u.balance}")


executor.start_polling(dp)