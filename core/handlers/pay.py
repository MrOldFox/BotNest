from aiogram import Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, ShippingOption, ShippingQuery

from core.keyboards.inline import *

async def order(message: Message, bot: Bot):
    await bot.send_message(message.chat.id,
                    f'\nДля проведения пробной покупки используйте данные тестовой карты:'\
                    f'\n<b>Номер карты</b>: <code>1111 1111 1111 1026</code>'\
                    f'\n<b>Дата выпуска</b>: 12/22'\
                    f'\n<b>CVC</b>: 000', parse_mode='HTML')
    await bot.send_invoice(
        chat_id=message.chat.id,
        title='Тестовая покупка в Телеграм',
        description=f'Тестовая покупка в телеграм боте',
        payload='Test payment',
        provider_token='381764678:TEST:73182',
        currency='rub',
        prices=[
            LabeledPrice(
                label='Доступ к тестовой покупке',
                amount=10000
            ),
            LabeledPrice(
                label='НДС',
                amount=5000
            ),
            LabeledPrice(
                label='Скидка',
                amount=-5000
            ),
            LabeledPrice(
                label='Бонус',
                amount=-1000
            )
        ],
        max_tip_amount=100,
        suggested_tip_amounts=[10, 50, 100],
        start_parameter='nztcoder',
        provider_data=None,
        photo_url='',
        photo_size=None,
        photo_width=None,
        need_name=False,
        need_phone_number=False,
        need_shipping_address=False,
        need_email=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False, #цена зависит от места доставки
        disable_notification=False,
        protect_content=False, #защита от пересылки
        reply_to_message_id=None, #цититровать какое-то сообщение на оплату
        allow_sending_without_reply=True,
        reply_markup=None, #передать клавиатуру при оплате
        request_timeout=15
    )


async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def successful_payment(message: Message):
    msg = f'Вы успешно получили пробную оплату товара, при этом вы потратили {message.successful_payment.total_amount // 100} виртуальных {message.successful_payment.currency}.' \
          f'\nЕсли  хотите получить такой же бот, то можете подать заявку здесь'
    await message.answer(msg)




RUS_SHIPPING = ShippingOption(
    id='ru',
    title='Доставка по России',
    prices=[
        LabeledPrice(
            label='Доставка по России',
            amount=2000
        )
    ]
)

TUM_SHIPPING = ShippingOption(
    id='tum',
    title='Доставка по Тюмени',
    prices=[
        LabeledPrice(
            label='Доставка по Тюмени',
            amount=500
        )
    ]
)


async def shipping_check(shipping_query: ShippingQuery, bot: Bot):
    shipping_options = []
    country = ['RU']
    cities = ['Тюмень']
    if shipping_query.shipping_address.country_code not in country:
        return await bot.answer_shipping_query(shipping_query.id, ok=False,
                                               error_message='Доставки в данный город пока нет')
    if shipping_query.shipping_address.country_code == 'TUM':
        shipping_options.append(TUM_SHIPPING)

    if shipping_query.shipping_address.city in cities:
        shipping_options.append(TUM_SHIPPING)

    await bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options)


async def order_cities(message: Message, bot: Bot):
    await bot.send_message(message.chat.id,
                    f'\nДля проведения пробной покупки используйте данные тестовой карты:'\
                    f'\n<b>Номер карты</b>: <code>1111 1111 1111 1026</code>'\
                    f'\n<b>Дата выпуска</b>: 12/22'\
                    f'\n<b>CVC</b>: 000', parse_mode='HTML')
    await bot.send_invoice(
        chat_id=message.chat.id,
        title='Тестовая покупка в Телеграм',
        description=f'Тестовая покупка в телеграм боте',
        payload='Test payment',
        provider_token='381764678:TEST:73182',
        currency='rub',
        prices=[
            LabeledPrice(
                label='Доступ к тестовой покупке',
                amount=10000
            ),
            LabeledPrice(
                label='НДС',
                amount=5000
            ),
            LabeledPrice(
                label='Скидка',
                amount=-5000
            ),
            LabeledPrice(
                label='Бонус',
                amount=-1000
            )
        ],
        max_tip_amount=100,
        suggested_tip_amounts=[10, 50, 100],
        start_parameter='nztcoder',
        provider_data=None,
        photo_url='',
        photo_size=None,
        photo_width=None,
        need_name=False,
        need_phone_number=True,
        need_shipping_address=True,
        need_email=True,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=True, #цена зависит от места доставки
        disable_notification=False,
        protect_content=False, #защита от пересылки
        reply_to_message_id=None, #цититровать какое-то сообщение на оплату
        allow_sending_without_reply=True,
        reply_markup=buy, #передать клавиатуру при оплате
        request_timeout=15
    )