from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from config import TOKENTGAPI


storage = MemoryStorage()
bot = Bot(TOKENTGAPI)
dp = Dispatcher(bot, storage=storage)


class UploadStatesGroup(StatesGroup):
    name = State()
    photo = State()
    artists = State()
    typerelise = State()
    track = State()
    description = State()
    check = State()


def get_upload_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("/upload"))
    return kb

def get_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    return kb

def get_cancel_kb(kb=ReplyKeyboardMarkup(resize_keyboard=True)) -> ReplyKeyboardMarkup:
    kb.add(KeyboardButton("/cancel"))
    return kb

def get_tipe_relise_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Сингл")).add(KeyboardButton("Альбом"))
    return kb

def get_check_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Да")).add(KeyboardButton("Нет, отменить"))
    return kb


@dp.message_handler(state="*", commands="cancel")
async def cmd_cancel(message: types.Message, state: FSMContext) -> None:
    current_state=state.get_state()
    if current_state is None:
        return
    await message.reply("Отменено",
                        reply_markup=get_upload_kb())
    await state.finish()

@dp.message_handler(state=UploadStatesGroup.name, content_types="text")
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer("Теперь скинь обложку для трека. Ее необходимо отправить как файл.\n\n Обложка должна быть в разрешении 3000х3000 и в хорошем качестве.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    await UploadStatesGroup.next()

@dp.message_handler(state=UploadStatesGroup.name, content_types="any")
async def check_name(message: types.Message, state: FSMContext) -> None:
    await message.reply("Что то не так. Введи название трека.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))

@dp.message_handler(state=UploadStatesGroup.photo, content_types=["document"])
async def load_photo(message: types.Message, state: FSMContext) -> None:
    if message.document.mime_base == "image": 
        async with state.proxy() as data:
            data["photo"] = message.document.file_id
        await message.answer("Отлично, теперь укажи исполнителя, если исполнителей несколько, то укажи их через запятую друг за другом",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
        await UploadStatesGroup.next()
    else:
        await message.reply("Пожалуйста, отправьте именно обложку.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))

@dp.message_handler(state=UploadStatesGroup.photo, content_types="any")
async def check_photo(message: types.Message, state: FSMContext) -> None:
    await message.reply("Пожалуйста, отправьте обложку как файл(документ)",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    
@dp.message_handler(state=UploadStatesGroup.artists, content_types="text")
async def load_artists(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["artists"] = message.text
    await message.answer("Теперь выбери тип релиза(Сингл или Альбом)",
                         reply_markup=get_cancel_kb(get_tipe_relise_kb()))
    await UploadStatesGroup.next()

@dp.message_handler(state=UploadStatesGroup.artists, content_types="any")
async def check_artists(message: types.Message, state: FSMContext) -> None:
    await message.reply("Что то не так. Введи никнеймы артистов через запятую.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    
@dp.message_handler(lambda message: message.text in ["Сингл", "Альбом"], state=UploadStatesGroup.typerelise, content_types="text")
async def load_typerelise(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["typerelise"] = message.text
    await message.answer("Теперь скинь wav своего трека. Файл должен быть стерео, 44100гц",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    await UploadStatesGroup.next()

@dp.message_handler(state=UploadStatesGroup.typerelise, content_types="any")
async def check_typerelise(message: types.Message, state: FSMContext) -> None:
    await message.reply("Что то не так. Введи либо Сингл, либо Альбом",
                         reply_markup=get_cancel_kb(get_tipe_relise_kb()))
    
@dp.message_handler(state=UploadStatesGroup.track, content_types=["document"])
async def load_track(message: types.Message, state: FSMContext) -> None:
    if message.document.mime_subtype == "x-wav": 
        async with state.proxy() as data:
            data["track"] = message.document.file_id
        await message.answer("Сейчас вам необходимо оставить комментарий с доп информацией. И указать:\n"+
                             "\n1) Нуждаетесь ли Вы в дополнительных услугах (бендлинк, карточка музыканта)?"+
                             "\n2) Нуждается ли Ваш релиз в промо-поддержке(Питчинге)?"+
                             "\n3) Дата выпуска релиза(Не раньше 3 дней. При промо не раньше 2 недель от даты создания анкеты.)"+
                             "\n4) В случае если вам необходимо отметить автора бита так же напишите это тут под этим пунктом."+
                             "\n\nА так же любую информацию которую вы считаете нужной для дополнения к релизу.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
        await UploadStatesGroup.next()
    else:
        await message.reply("Пожалуйста, отправьте именно wav файл.",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))

@dp.message_handler(state=UploadStatesGroup.track, content_types="any")
async def check_track(message: types.Message, state: FSMContext) -> None:
    await message.reply("Пожалуйста, отправьте трек как файл(документ)",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    
@dp.message_handler(state=UploadStatesGroup.description, content_types="text")
async def load_description(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["description"] = message.text
    await message.answer("Все данные верны?(Введи либо Да, либо Нет, отменить)",
                         reply_markup=get_cancel_kb(get_check_kb()))
    async with state.proxy() as data:
        await bot.send_message(chat_id=message.from_user.id,
                                text =  "Название трека: " + data["name"] +"\n"+
                                        "Исполнители: " + data["artists"]+"\n"+
                                        "Тип релиза: "+data["typerelise"]+"\n"+
                                        "Дополнительно:"+data["description"])
        await bot.send_document(chat_id=message.from_user.id,
                                document=data["photo"])
        await bot.send_document(chat_id=message.from_user.id,
                                document=data["track"])

    await UploadStatesGroup.next()

@dp.message_handler(state=UploadStatesGroup.description, content_types="any")
async def load_description(message: types.Message, state: FSMContext) -> None:
    await message.answer("Описание поддерживает только текст. Не кидай файлы)",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    
@dp.message_handler(lambda message: message.text in ["Да", "Нет, отменить"], state=UploadStatesGroup.check, content_types="text")
async def load_typerelise(message: types.Message, state: FSMContext) -> None:
    if message.text == "Нет, отменить":
        await message.reply("Заявка отменена",
                         reply_markup=get_upload_kb())
    else:
        username="Пустой юзер"
        try:
            username = message.from_user.username
        except ValueError:
            print("Ошибка с именем пользователя!")
        async with state.proxy() as data:
            await bot.send_message(chat_id=218957780,
                                    text =  "Заявка от: @" +  str(username) +"\n"+
                                            "Название трека: " + data["name"] +"\n"+
                                            "Исполнители: " + data["artists"]+"\n"+
                                            "Тип релиза: "+ data["typerelise"]+"\n"+
                                            "Дополнительно: "+data["description"])
            await bot.send_document(chat_id=218957780,
                                    document=data["photo"])
            await bot.send_document(chat_id=218957780,
                                    document=data["track"])
        await message.answer("Заявка отправлена", reply_markup=get_upload_kb())

    await state.finish()


@dp.message_handler(state=UploadStatesGroup.check, content_types="any")
async def load_typerelise(message: types.Message, state: FSMContext) -> None:
    await message.reply("Что то не так. Введи либо Да, либо Нет, отменить",
                         reply_markup=get_cancel_kb(get_check_kb()))


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message) -> None:
    await message.answer("Привет! \n\nЯ бот лейбла string base, и я помогу тебе загрузить свой трек на все площадки вместе с нами." + 
                         "\n\nДля загрузки трека введи команду \n/upload",
                         reply_markup=get_upload_kb())

@dp.message_handler(commands=["upload"])
async def cmd_upload(message: types.Message) -> None:
    await message.answer("Напишите название вашего трека",
                         reply_markup=get_cancel_kb(ReplyKeyboardMarkup(resize_keyboard=True)))
    await UploadStatesGroup.name.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = False)