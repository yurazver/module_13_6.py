
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = '*************'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

kb = InlineKeyboardMarkup()
button = InlineKeyboardButton(text = 'Информация', callback_data = 'info')
kb.add(button)


class Form(StatesGroup):
    age = State()
    weight = State()
    growth = State()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Рассчитать').add('Информация')
    await message.answer("Выберите опцию:", reply_markup = keyboard)


@dp.message_handler(text ='Рассчитать')
async def main_menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    button_calories = types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
    button_formulas = types.InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')

    keyboard.add(button_calories, button_formulas)
    await message.answer("Выберите опцию:", reply_markup=keyboard)



@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "Формула Миффлина-Сан Жеора:\n "
        "Для мужчин:\nBMR = 10 * масса(кг) + 6.25 * рост(см) - 5 * возраст(годы) + 5 "
        "Для женщин:\nBMR = 10 * масса(кг) + 6.25 * рост(см) - 5 * возраст(годы) - 161 ")


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.answer()
    await Form.age.set()
    await call.message.answer("Введите ваш возраст:")


@dp.message_handler(state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    age = int(message.text)
    await state.update_data(age=age)
    await Form.growth.set()
    await message.answer("Введите ваш рост (см):")

@dp.message_handler(state=Form.growth)
async def process_growth(message: types.Message, state: FSMContext):
    growth = int(message.text)
    await state.update_data(growth=growth)
    await Form.weight.set()
    await message.answer("Введите ваш вес (кг):")



@dp.message_handler(state=Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    weight = int(message.text)
    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')

    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.reply(f"Ваша суточная норма калорий: {calories:.2f}")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)