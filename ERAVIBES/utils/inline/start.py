from pyrogram.types import InlineKeyboardButton

import config
from ERAVIBES import app



def start_pannel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="❖ ᴛᴧᴘ тᴏ sᴇᴇ ᴍᴧɢɪᴄ ❖",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="• ʜᴇʟᴘ •", callback_data="settings_back_helper"),
            InlineKeyboardButton(text="• sᴇᴛ •", callback_data="settings_helper"),
        ],
        [
            InlineKeyboardButton(text="• sᴏᴜꝛᴄᴇ •", url=config.SUPPORT_CHAT),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text=_["S_B_5"], url=f"https://t.me/MCYDMBOT?start"),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT),
        ],
       [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
    ]
    return buttons
