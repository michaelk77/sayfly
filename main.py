import autopep8
from aiogram import Bot, types
from threading import Thread
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from subprocess import run, PIPE
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, select, update
import telebot

logbot = telebot.TeleBot('Your id')# бот для логирования
admin = "Your id"
TOKEN = "Token"
metadata = MetaData()
engine = create_engine(
    "postgresql://youradress")
Usersinfo = Table("Usersinfo", metadata,
                  Column('id', Integer(), primary_key=True),
                  Column('userid', String(100), unique=True, nullable=False),
                  Column('inter', String(100), nullable=False),
                  Column("time", Integer()), Column('librarys', String(200)))

metadata.create_all(engine)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
inline_btn_2 = InlineKeyboardButton('Поехали!', callback_data='button3')
inline_kb2 = InlineKeyboardMarkup().add(inline_btn_2)
z = KeyboardButton('Выполнение')
z2 = KeyboardButton('Pep-8')
z3 = KeyboardButton('Настройка')
key = ReplyKeyboardMarkup(True, True).add(z, z2)
key.add(z3)

timehelp = {}


class Form(StatesGroup):
    prog = State()
    vvod = State()
    pep = State()


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


@dp.message_handler(state=Form.pep)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logbot.send_message(admin, str(message))
        z = message.text
        await bot.send_message(message.from_user.id, "Редактирую")
        y = z.splitlines()
        for i in range(len(y)):
            kol = 0
            kol1 = 0
            if "print" in y[i]:
                j = 0
                while j < len(y[i]):
                    if "\"" == y[i][j]:
                        kol += 1
                    if "\'" == y[i][j]:
                        kol1 += 1
                    if kol % 2 == 0 and kol1 % 2 == 0 and y[i][j] in "+-**//":
                        if y[i][j + 1] == y[i][j]:
                            y[i] = y[i][:j] + \
                                   f" {y[i][j] + y[i][j]} " + y[i][j + 2:]
                            j += 3
                        else:
                            y[i] = y[i][:j] + f" {y[i][j]} " + y[i][j + 1:]
                            j += 2
                    j += 1
        z = "\n".join(y)
        z = autopep8.fix_code(z, options={'aggressive': 10000})
        await bot.send_message(message.from_user.id, z)
        await state.set_state()
        await state.finish()


@dp.message_handler(state=Form.prog)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logbot.send_message(admin, str(message))
        if message.from_user.id not in timehelp:
            updatebd(message.from_user.id)
        id = str(message.from_user.id)
        z = message.text
        r = open("prog" + str(message.from_user.id) +
                 ".py", "w", encoding="UTF-8")
        print(z)
        if "main.py" in z or "prog" in z or "project_sayfly" in z:
            await bot.send_message(message.from_user.id,
                                   "Мы сами используем такие названия файлов(main или prog или project_sayfly), пожалуйста "
                                   "переменуйти "
                                   "свои файлы или переменные", reply_markup=key)
            await state.set_state()
            await state.finish()
            return

        if "math" in timehelp[id]["librarys"].split():
            print("import math\n", file=r)
        if "numpy" in timehelp[id]["librarys"].split():
            print("import numpy\n", file=r)
        if "pandas" in timehelp[id]["librarys"].split():
            print("import pandas\n", file=r)
        print("""import importlib
import sys

def secure_importer(name, globals=None, locals=None, fromlist=(), level=0):
    if name:
        print("a nelisea")
        raise ImportError("module '%s' is restricted." % name)


__builtins__.__dict__['__import__'] = secure_importer""",
              file=r)
        print(
            "sys.modules['os']=None\nsys.modules['requests']=None\nsys.modules["
            "'socket']=None\nsys.modules['subprocess']=None\nsys.modules['webbrowser']=None\nsys.modules["
            "'flask']=None\nsys.modules['antigravity']=None\nsys.modules['sqlalchemy']=None\nsys.modules["
            "'psycopg2']=None\n", file=r)
        print(z, file=r)
        r.close()
        if "input" in z or "stdin" in z:
            await bot.send_message(message.from_user.id, "Введите полные данные ввода")
            await Form.vvod.set()
        else:
            solution = run([timehelp[id]["inter"], "prog" + str(message.from_user.id) + ".py"],
                           stdout=PIPE,
                           encoding="UTF-8", stderr=PIPE,
                           text=True, timeout=timehelp[id]["time"])
            if solution.stderr:
                await bot.send_message(message.from_user.id, solution.stderr)
            else:
                if solution.stdout:
                    await bot.send_message(message.from_user.id, solution.stdout)
                else:
                    await bot.send_message(message.from_user.id, "Ваша программа не вернула никакого текста")
            await state.set_state()
            await state.finish()


@dp.message_handler(state=Form.vvod)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        logbot.send_message(admin, str(message))
        solution = run(["python3", "prog" + str(message.from_user.id) + ".py"],
                       stdout=PIPE,
                       encoding="UTF-8", stderr=PIPE, input=message.text,
                       text=True, timeout=3)
        if solution.stderr:
            await bot.send_message(message.from_user.id, solution.stderr)
        else:
            if solution.stdout:
                await bot.send_message(message.from_user.id, solution.stdout)
            else:
                await bot.send_message(message.from_user.id, "Ваша программа не вернула никакого текста")
        await state.set_state()
        await state.finish()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    logbot.send_message(admin, str(message))
    global timehelp
    await message.reply(
        "Привет👋\n\nЯ бот для программирования от создателя @Py_mk_bot\n\nЧто же тут такого нового что нужен "
        "отдельный бот?\nУпрощенный функционал\nПовышенная безопасность\nОставленны только самые важные "
        "функции\nБольшая возможность для подстройки\nУниверсальность для каждого\n\nSayfly - safe and friendly",
        reply_markup=inline_kb2)
    updatebd(message.from_user.id)


@dp.callback_query_handler(text='button3')
async def process_hi2_command(query: types.CallbackQuery):
    await query.answer()
    await bot.send_message(query.from_user.id, "Выполнение - функция для выполнения ваших програм\nPep-8 - "
                                               "функция которая после отправки боту кода программы "
                                               "отформатирует код по данному стандарту\nНастройка - настройка "
                                               "интерпретатора для выполнения вашей программы", reply_markup=key)


@dp.message_handler(text="Выполнение")
async def process_start_command(message: types.Message):
    logbot.send_message(admin, str(message))
    await Form.prog.set()
    await message.reply(
        "Отправьте вашу программу для выполнения:")


@dp.message_handler(text="Pep-8")
async def process_start_command(message: types.Message):
    logbot.send_message(admin, str(message))
    await Form.pep.set()
    await message.reply(
        "Отправьте вашу программу для редактирования:")


@dp.callback_query_handler(text='python')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        inter="python"))
    print(query.from_user.id, "python")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='python3')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        inter="python3"))
    print(query.from_user.id, "python3")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='3')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        time="3"))
    print(query.from_user.id, "3")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='5')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        time="5"))
    print(query.from_user.id, "5")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='15')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        time="15"))
    print(query.from_user.id, "15")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='30')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
        time="30"))
    print(query.from_user.id, "30")
    await query.answer("Success")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='math')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    r = conn.execute(select([Usersinfo]).where(
        Usersinfo.c.userid == str(query.from_user.id)))
    lib = r.first()[-1]
    if "math" in lib:
        s = lib.split()
        del s[s.index("math")]
        print(query.from_user.id, "math")
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=" ".join(s)))
        await query.answer("Noimport")
    else:
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=lib + " math"))
        print(query.from_user.id, "math")
        await query.answer("Inimport")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='numpy')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    r = conn.execute(select([Usersinfo]).where(
        Usersinfo.c.userid == str(query.from_user.id)))
    lib = r.first()[-1]
    if "numpy" in lib:
        s = lib.split()
        del s[s.index("numpy")]
        print(query.from_user.id, "numpy")
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=" ".join(s)))
        await query.answer("Noimport")
    else:
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=lib + " numpy"))
        print(query.from_user.id, "numpy")
        await query.answer("Inimport")
    updatebd(query.from_user.id)


@dp.callback_query_handler(text='pandas')
async def process_hi2_command(query: types.CallbackQuery):
    conn = engine.connect()
    r = conn.execute(select([Usersinfo]).where(
        Usersinfo.c.userid == str(query.from_user.id)))
    lib = r.first()[-1]
    if "pandas" in lib:
        s = lib.split()
        del s[s.index("pandas")]
        print(query.from_user.id, "pandas")
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=" ".join(s)))
        await query.answer("Noimport")
    else:
        conn.execute(update(Usersinfo).where(Usersinfo.c.userid == str(query.from_user.id)).values(
            librarys=lib + " pandas"))
        print(query.from_user.id, "pandas")
        await query.answer("Inimport")
    updatebd(query.from_user.id)


@dp.message_handler(text="Настройка")
async def process_start_command(message: types.Message):
    logbot.send_message(admin, str(message))
    inline_btn_1 = InlineKeyboardButton('python2', callback_data='python')
    inline_btn_3 = InlineKeyboardButton('python3', callback_data='python3')
    inline_kb4 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_3)
    await bot.send_message(message.from_user.id, "Интерпритатор", reply_markup=inline_kb4)
    inline_btn_0 = InlineKeyboardButton('3', callback_data='3')
    inline_btn_03 = InlineKeyboardButton('5', callback_data='5')
    inline_btn_4 = InlineKeyboardButton('15', callback_data='15')
    inline_btn_5 = InlineKeyboardButton('30', callback_data='30')
    inline_kb7 = InlineKeyboardMarkup().add(
        inline_btn_0, inline_btn_03, inline_btn_4, inline_btn_5)
    await bot.send_message(message.from_user.id,
                           "Максимальное время выполнения(не спишите его увеличивать, если в вашей программе ошибка "
                           "то вам придеться прождать это время в сек)",
                           reply_markup=inline_kb7)
    inline_btn_0 = InlineKeyboardButton('math', callback_data='math')
    inline_btn_03 = InlineKeyboardButton('numpy', callback_data='numpy')
    inline_btn_4 = InlineKeyboardButton('pandas', callback_data='pandas')
    inline_lib = InlineKeyboardMarkup().add(
        inline_btn_0, inline_btn_03, inline_btn_4)
    await bot.send_message(message.from_user.id,
                           "Библиотеки которые будут импортированны по умолчанию, по нажатию меняеться применять или "
                           "нет, sys уже импортирован",
                           reply_markup=inline_lib)
    await bot.send_message(message.from_user.id,
                           "Поддержка - @mkpythonbk (можете запросить новые библиотеки)")


def updatebd(id): # Значительное ускорение бд если проект и сервер в разных местах, НЕ НУЖНО ЕСЛИ У ВАС ВСЕ В ОДНОМ МЕСТЕ
    try:
        conn = engine.connect()
        r = conn.execute(select([Usersinfo]).where(
            Usersinfo.c.userid == str(id)))
        stroka = r.first()
        if not stroka:
            ins = conn.execute(
                Usersinfo.insert().values(userid=str(id), inter="python3", time=3, librarys=""))
            timehelp[str(id)] = {"inter": "python3", "time": 3, "librarys": ""}
        else:
            timehelp[str(id)] = {"inter": stroka[2],
                                 "time": stroka[3], "librarys": stroka[4]}
    except:
        try:
            ins = conn.execute(
                Usersinfo.insert().values(userid=str(id), inter="python3", time=3, librarys=""))
            timehelp[str(id)] = {"inter": "python3", "time": 3, "librarys": ""}
        except:
            pass


if __name__ == '__main__':
    Thread(target=keep_alive).start()
    executor.start_polling(dp, on_startup=print("start"))
