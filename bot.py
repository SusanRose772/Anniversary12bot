import os
import logging
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# ==================== CONFIGURATION ====================
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logging.error("❌ BOT_TOKEN environment variable is not set!")
    exit(1)

# ==================== LOGGING ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== EVENT DATABASE ====================
# Global events and anniversaries by month
EVENTS = {
    "January": [
        {"day": 1, "event": "🎉 New Year's Day", "country": "Global", "category": "🎉 Holiday"},
        {"day": 4, "event": "🏛️ Independence Day (Myanmar)", "country": "Myanmar", "category": "🏛️ Political"},
        {"day": 10, "event": "⚖️ National Human Trafficking Awareness Day", "country": "USA", "category": "🌐 Awareness"},
        {"day": 15, "event": "🕊️ Martin Luther King Jr. Day", "country": "USA", "category": "📅 Historical"},
        {"day": 26, "event": "🇦🇺 Australia Day", "country": "Australia", "category": "🎉 Holiday"},
        {"day": 27, "event": "🕊️ International Holocaust Remembrance Day", "country": "Global", "category": "📅 Historical"}
    ],
    "February": [
        {"day": 2, "event": "🇺🇸 Groundhog Day", "country": "USA", "category": "🎉 Cultural"},
        {"day": 4, "event": "🇱🇰 Independence Day (Sri Lanka)", "country": "Sri Lanka", "category": "🏛️ Political"},
        {"day": 11, "event": "🇯🇵 National Foundation Day", "country": "Japan", "category": "🏛️ Political"},
        {"day": 14, "event": "💕 Valentine's Day", "country": "Global", "category": "🎉 Cultural"},
        {"day": 21, "event": "🌐 International Mother Language Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 23, "event": "🇷🇺 Defender of the Fatherland Day", "country": "Russia", "category": "🏛️ Political"}
    ],
    "March": [
        {"day": 1, "event": "🇰🇷 Independence Movement Day", "country": "South Korea", "category": "🏛️ Political"},
        {"day": 3, "event": "🇧🇬 Liberation Day", "country": "Bulgaria", "category": "🏛️ Political"},
        {"day": 6, "event": "🇬🇭 Ghana Independence Day", "country": "Ghana", "category": "🏛️ Political"},
        {"day": 8, "event": "👩 International Women's Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 12, "event": "🇲🇺 Mauritius Day", "country": "Mauritius", "category": "🏛️ Political"},
        {"day": 17, "event": "🍀 St. Patrick's Day", "country": "Ireland", "category": "🎉 Cultural"},
        {"day": 20, "event": "🌍 International Day of Happiness", "country": "Global", "category": "🌐 Awareness"},
        {"day": 21, "event": "🌳 International Day of Forests", "country": "Global", "category": "🌐 Awareness"},
        {"day": 23, "event": "🇵🇰 Pakistan Day", "country": "Pakistan", "category": "🏛️ Political"},
        {"day": 25, "event": "🇬🇷 Greek Independence Day", "country": "Greece", "category": "🏛️ Political"},
        {"day": 26, "event": "🇧🇩 Bangladesh Independence Day", "country": "Bangladesh", "category": "🏛️ Political"}
    ],
    "April": [
        {"day": 1, "event": "🤡 April Fool's Day", "country": "Global", "category": "🎉 Cultural"},
        {"day": 4, "event": "🇸🇳 Senegal Independence Day", "country": "Senegal", "category": "🏛️ Political"},
        {"day": 7, "event": "🌍 World Health Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 12, "event": "🚀 International Day of Human Space Flight", "country": "Global", "category": "🌐 Awareness"},
        {"day": 14, "event": "🇬🇪 Georgia Independence Day", "country": "Georgia", "category": "🏛️ Political"},
        {"day": 17, "event": "🇸🇾 Independence Day (Syria)", "country": "Syria", "category": "🏛️ Political"},
        {"day": 18, "event": "🇿🇼 Zimbabwe Independence Day", "country": "Zimbabwe", "category": "🏛️ Political"},
        {"day": 22, "event": "🌍 Earth Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 25, "event": "🇵🇹 Revolution Day (Portugal)", "country": "Portugal", "category": "🏛️ Political"},
        {"day": 27, "event": "🇸🇱 Sierra Leone Independence Day", "country": "Sierra Leone", "category": "🏛️ Political"},
        {"day": 30, "event": "🇳🇱 King's Day (Netherlands)", "country": "Netherlands", "category": "🎉 Cultural"}
    ],
    "May": [
        {"day": 1, "event": "👷 International Workers' Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 4, "event": "🇳🇱 Remembrance Day (Netherlands)", "country": "Netherlands", "category": "📅 Historical"},
        {"day": 5, "event": "🇰🇷 Children's Day (South Korea)", "country": "South Korea", "category": "🎉 Cultural"},
        {"day": 8, "event": "🕊️ VE Day (WWII Victory)", "country": "Europe", "category": "📅 Historical"},
        {"day": 9, "event": "🇷🇺 Victory Day (Russia)", "country": "Russia", "category": "🏛️ Political"},
        {"day": 12, "event": "🌍 International Nurses Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 14, "event": "🇮🇱 Independence Day (Israel)", "country": "Israel", "category": "🏛️ Political"},
        {"day": 15, "event": "🇵🇾 Independence Day (Paraguay)", "country": "Paraguay", "category": "🏛️ Political"},
        {"day": 17, "event": "🇳🇴 Constitution Day (Norway)", "country": "Norway", "category": "🏛️ Political"},
        {"day": 20, "event": "🇨🇲 Cameroon National Day", "country": "Cameroon", "category": "🏛️ Political"},
        {"day": 22, "event": "🇾🇪 Unity Day (Yemen)", "country": "Yemen", "category": "🏛️ Political"},
        {"day": 25, "event": "🇦🇷 Argentina National Day", "country": "Argentina", "category": "🏛️ Political"}
    ],
    "June": [
        {"day": 1, "event": "👶 International Children's Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 2, "event": "🇮🇹 Republic Day (Italy)", "country": "Italy", "category": "🏛️ Political"},
        {"day": 5, "event": "🌍 World Environment Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 6, "event": "🇸🇪 National Day (Sweden)", "country": "Sweden", "category": "🏛️ Political"},
        {"day": 10, "event": "🇵🇹 Portugal Day", "country": "Portugal", "category": "🏛️ Political"},
        {"day": 12, "event": "🇵🇭 Independence Day (Philippines)", "country": "Philippines", "category": "🏛️ Political"},
        {"day": 14, "event": "🇺🇸 Flag Day (USA)", "country": "USA", "category": "🏛️ Political"},
        {"day": 17, "event": "🇮🇸 National Day (Iceland)", "country": "Iceland", "category": "🏛️ Political"},
        {"day": 20, "event": "🌍 World Refugee Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 21, "event": "🌞 International Yoga Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 25, "event": "🇲🇿 Independence Day (Mozambique)", "country": "Mozambique", "category": "🏛️ Political"},
        {"day": 27, "event": "🇩🇯 Independence Day (Djibouti)", "country": "Djibouti", "category": "🏛️ Political"}
    ],
    "July": [
        {"day": 1, "event": "🇨🇦 Canada Day", "country": "Canada", "category": "🏛️ Political"},
        {"day": 4, "event": "🇺🇸 Independence Day (USA)", "country": "USA", "category": "🏛️ Political"},
        {"day": 5, "event": "🇻🇪 Independence Day (Venezuela)", "country": "Venezuela", "category": "🏛️ Political"},
        {"day": 9, "event": "🇦🇷 Independence Day (Argentina)", "country": "Argentina", "category": "🏛️ Political"},
        {"day": 11, "event": "🇲🇳 Revolution Day (Mongolia)", "country": "Mongolia", "category": "🏛️ Political"},
        {"day": 14, "event": "🇫🇷 Bastille Day", "country": "France", "category": "🏛️ Political"},
        {"day": 17, "event": "🇮🇶 Republic Day (Iraq)", "country": "Iraq", "category": "🏛️ Political"},
        {"day": 20, "event": "🇨🇴 Independence Day (Colombia)", "country": "Colombia", "category": "🏛️ Political"},
        {"day": 21, "event": "🇧🇪 National Day (Belgium)", "country": "Belgium", "category": "🏛️ Political"},
        {"day": 23, "event": "🇪🇬 Revolution Day (Egypt)", "country": "Egypt", "category": "🏛️ Political"},
        {"day": 25, "event": "🇵🇷 Constitution Day (Puerto Rico)", "country": "Puerto Rico", "category": "🏛️ Political"},
        {"day": 28, "event": "🇵🇪 Independence Day (Peru)", "country": "Peru", "category": "🏛️ Political"},
        {"day": 30, "event": "🇲🇦 Throne Day (Morocco)", "country": "Morocco", "category": "🏛️ Political"}
    ],
    "August": [
        {"day": 1, "event": "🇨🇭 National Day (Switzerland)", "country": "Switzerland", "category": "🏛️ Political"},
        {"day": 5, "event": "🇧🇫 Independence Day (Burkina Faso)", "country": "Burkina Faso", "category": "🏛️ Political"},
        {"day": 6, "event": "🇯🇲 Independence Day (Jamaica)", "country": "Jamaica", "category": "🏛️ Political"},
        {"day": 7, "event": "🇨🇮 Independence Day (Ivory Coast)", "country": "Ivory Coast", "category": "🏛️ Political"},
        {"day": 9, "event": "🇸🇬 National Day (Singapore)", "country": "Singapore", "category": "🏛️ Political"},
        {"day": 11, "event": "🇨🇱 Independence Day (Chile)", "country": "Chile", "category": "🏛️ Political"},
        {"day": 14, "event": "🇵🇰 Independence Day (Pakistan)", "country": "Pakistan", "category": "🏛️ Political"},
        {"day": 15, "event": "🇰🇷 Liberation Day (South Korea)", "country": "South Korea", "category": "🏛️ Political"},
        {"day": 17, "event": "🇮🇩 Independence Day (Indonesia)", "country": "Indonesia", "category": "🏛️ Political"},
        {"day": 19, "event": "🇦🇫 Independence Day (Afghanistan)", "country": "Afghanistan", "category": "🏛️ Political"},
        {"day": 25, "event": "🇺🇾 Independence Day (Uruguay)", "country": "Uruguay", "category": "🏛️ Political"},
        {"day": 27, "event": "🇲🇩 Independence Day (Moldova)", "country": "Moldova", "category": "🏛️ Political"},
        {"day": 29, "event": "🇸🇰 National Uprising Day", "country": "Slovakia", "category": "📅 Historical"},
        {"day": 31, "event": "🇲🇾 Independence Day (Malaysia)", "country": "Malaysia", "category": "🏛️ Political"}
    ],
    "September": [
        {"day": 1, "event": "🇺🇿 Independence Day (Uzbekistan)", "country": "Uzbekistan", "category": "🏛️ Political"},
        {"day": 2, "event": "🇻🇳 Independence Day (Vietnam)", "country": "Vietnam", "category": "🏛️ Political"},
        {"day": 3, "event": "🇶🇦 National Day (Qatar)", "country": "Qatar", "category": "🏛️ Political"},
        {"day": 7, "event": "🇧🇷 Independence Day (Brazil)", "country": "Brazil", "category": "🏛️ Political"},
        {"day": 9, "event": "🇰🇵 National Day (North Korea)", "country": "North Korea", "category": "🏛️ Political"},
        {"day": 10, "event": "🇧🇿 Independence Day (Belize)", "country": "Belize", "category": "🏛️ Political"},
        {"day": 15, "event": "🇨🇷 Independence Day (Costa Rica)", "country": "Costa Rica", "category": "🏛️ Political"},
        {"day": 16, "event": "🇲🇽 Independence Day (Mexico)", "country": "Mexico", "category": "🏛️ Political"},
        {"day": 18, "event": "🇨🇱 Independence Day (Chile)", "country": "Chile", "category": "🏛️ Political"},
        {"day": 19, "event": "🇰🇳 Independence Day (St. Kitts)", "country": "St. Kitts", "category": "🏛️ Political"},
        {"day": 21, "event": "🇧🇿 Independence Day (Armenia)", "country": "Armenia", "category": "🏛️ Political"},
        {"day": 23, "event": "🇸🇦 Saudi National Day", "country": "Saudi Arabia", "category": "🏛️ Political"},
        {"day": 30, "event": "🇧🇼 Botswana Independence Day", "country": "Botswana", "category": "🏛️ Political"}
    ],
    "October": [
        {"day": 1, "event": "🇨🇳 China National Day", "country": "China", "category": "🏛️ Political"},
        {"day": 2, "event": "🇮🇳 Gandhi Jayanti (India)", "country": "India", "category": "📅 Historical"},
        {"day": 3, "event": "🇩🇪 Unity Day (Germany)", "country": "Germany", "category": "🏛️ Political"},
        {"day": 4, "event": "🇱🇸 Lesotho Independence Day", "country": "Lesotho", "category": "🏛️ Political"},
        {"day": 5, "event": "🇵🇹 Republic Day (Portugal)", "country": "Portugal", "category": "🏛️ Political"},
        {"day": 9, "event": "🇺🇬 Uganda Independence Day", "country": "Uganda", "category": "🏛️ Political"},
        {"day": 10, "event": "🇨🇺 Independence Day (Cuba)", "country": "Cuba", "category": "🏛️ Political"},
        {"day": 12, "event": "🇪🇸 National Day (Spain)", "country": "Spain", "category": "🏛️ Political"},
        {"day": 14, "event": "🇾🇪 Yemen National Day", "country": "Yemen", "category": "🏛️ Political"},
        {"day": 24, "event": "🇺🇳 United Nations Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 26, "event": "🇦🇹 National Day (Austria)", "country": "Austria", "category": "🏛️ Political"},
        {"day": 27, "event": "🇹🇲 Independence Day (Turkmenistan)", "country": "Turkmenistan", "category": "🏛️ Political"},
        {"day": 29, "event": "🇹🇷 Republic Day (Turkey)", "country": "Turkey", "category": "🏛️ Political"}
    ],
    "November": [
        {"day": 1, "event": "🇩🇿 Revolution Day (Algeria)", "country": "Algeria", "category": "🏛️ Political"},
        {"day": 3, "event": "🇵🇦 Independence Day (Panama)", "country": "Panama", "category": "🏛️ Political"},
        {"day": 4, "event": "🇰🇼 National Day (Kuwait)", "country": "Kuwait", "category": "🏛️ Political"},
        {"day": 9, "event": "🇰🇭 Independence Day (Cambodia)", "country": "Cambodia", "category": "🏛️ Political"},
        {"day": 10, "event": "🇹🇷 Atatürk Remembrance Day", "country": "Turkey", "category": "📅 Historical"},
        {"day": 11, "event": "🕊️ Remembrance Day", "country": "Commonwealth", "category": "📅 Historical"},
        {"day": 18, "event": "🇱🇻 Independence Day (Latvia)", "country": "Latvia", "category": "🏛️ Political"},
        {"day": 22, "event": "🇱🇧 Independence Day (Lebanon)", "country": "Lebanon", "category": "🏛️ Political"},
        {"day": 25, "event": "🇸🇷 Independence Day (Suriname)", "country": "Suriname", "category": "🏛️ Political"},
        {"day": 28, "event": "🇲🇷 Independence Day (Mauritania)", "country": "Mauritania", "category": "🏛️ Political"},
        {"day": 30, "event": "🇧🇧 Independence Day (Barbados)", "country": "Barbados", "category": "🏛️ Political"}
    ],
    "December": [
        {"day": 1, "event": "🇷🇴 National Day (Romania)", "country": "Romania", "category": "🏛️ Political"},
        {"day": 2, "event": "🇦🇪 National Day (UAE)", "country": "UAE", "category": "🏛️ Political"},
        {"day": 5, "event": "🇹🇭 King's Birthday (Thailand)", "country": "Thailand", "category": "🏛️ Political"},
        {"day": 6, "event": "🇫🇮 Independence Day (Finland)", "country": "Finland", "category": "🏛️ Political"},
        {"day": 8, "event": "🇵🇦 Mother's Day (Panama)", "country": "Panama", "category": "🎉 Cultural"},
        {"day": 10, "event": "🌍 Human Rights Day", "country": "Global", "category": "🌐 Awareness"},
        {"day": 12, "event": "🇰🇪 Independence Day (Kenya)", "country": "Kenya", "category": "🏛️ Political"},
        {"day": 16, "event": "🇧🇩 Victory Day (Bangladesh)", "country": "Bangladesh", "category": "🏛️ Political"},
        {"day": 18, "event": "🇳🇪 Republic Day (Niger)", "country": "Niger", "category": "🏛️ Political"},
        {"day": 25, "event": "🎄 Christmas Day", "country": "Global", "category": "🎉 Cultural"},
        {"day": 26, "event": "🎄 Boxing Day", "country": "Commonwealth", "category": "🎉 Cultural"},
        {"day": 31, "event": "🎆 New Year's Eve", "country": "Global", "category": "🎉 Holiday"}
    ]
}

# ==================== USER DATA ====================
subscribed_chats: List[int] = []

# ==================== BOT COMMANDS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    user = update.effective_user
    user_id = update.effective_chat.id

    if user_id not in subscribed_chats:
        subscribed_chats.append(user_id)

    welcome_text = f"""🗓️ **Welcome to Anniversary Bot!**

Hi {user.first_name}! 👋

Your global event & anniversary tracker! Get updates on major events happening around the world.

🌍 **What we cover:**
• 🏛️ Political events & elections
• ⛪ Religious celebrations
• 🎓 Educational milestones
• 🎉 National holidays & festivals
• 📅 Historical anniversaries
• 🌐 International observances

📌 **Commands:**
/start - Welcome menu
/today - Events happening today
/upcoming - Upcoming events (7 days)
/country - Search events by country
/category - Browse by category
/subscribe - Get daily updates
/unsubscribe - Stop updates
/help - Need assistance?

📅 **Today's events:** Use /today to see what's happening!
"""

    keyboard = [
        [InlineKeyboardButton("📅 Today's Events", callback_data="today_events")],
        [InlineKeyboardButton("📆 Upcoming Events", callback_data="upcoming_events")],
        [InlineKeyboardButton("🌍 Browse by Country", callback_data="browse_country")],
        [InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's events"""
    today = datetime.now()
    month = today.strftime("%B")
    day = today.day

    events = EVENTS.get(month, [])
    today_events = [e for e in events if e["day"] == day]

    if today_events:
        message = f"📅 **Events Today - {today.strftime('%B %d, %Y')}**\n\n"
        for event in today_events:
            message += f"• {event['event']}\n"
            message += f"  📍 {event['country']} | {event['category']}\n\n"
    else:
        message = f"📅 **No major events today - {today.strftime('%B %d, %Y')}**\n\nCheck /upcoming for future events!"

    keyboard = [
        [InlineKeyboardButton("📆 Upcoming", callback_data="upcoming_events")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

async def upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show upcoming events (next 7 days)"""
    today = datetime.now()
    events_list = []
    
    for i in range(7):
        date = today + timedelta(days=i)
        month = date.strftime("%B")
        day = date.day
        events = EVENTS.get(month, [])
        day_events = [e for e in events if e["day"] == day]
        
        for event in day_events:
            events_list.append({
                "date": date.strftime("%B %d"),
                "event": event["event"],
                "country": event["country"],
                "category": event["category"]
            })

    if events_list:
        message = f"📆 **Upcoming Events (Next 7 Days)**\n\n"
        for event in events_list[:15]:
            message += f"📅 {event['date']}\n"
            message += f"• {event['event']}\n"
            message += f"  📍 {event['country']} | {event['category']}\n\n"
    else:
        message = "📆 **No upcoming events in the next 7 days.**"

    keyboard = [
        [InlineKeyboardButton("📅 Today", callback_data="today_events")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

async def country_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search events by country"""
    countries = set()
    for month_events in EVENTS.values():
        for event in month_events:
            countries.add(event["country"])
    
    countries = sorted(list(countries))[:20]
    
    message = "🌍 **Browse Events by Country**\n\nSend the country name to see events.\n\nExample: `Nigeria`, `USA`, `India`\n\n**Available countries:**\n"
    message += "• " + "\n• ".join(countries[:15])
    message += f"\n... and {len(countries) - 15} more."

    await update.message.reply_text(message, parse_mode="Markdown")

async def handle_country_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle country search from text input"""
    query = update.message.text.strip()
    
    found_events = []
    for month, month_events in EVENTS.items():
        for event in month_events:
            if query.lower() in event["country"].lower():
                found_events.append({
                    "month": month,
                    "event": event["event"],
                    "day": event["day"],
                    "country": event["country"],
                    "category": event["category"]
                })

    if found_events:
        message = f"🌍 **Events in {query}**\n\n"
        for event in found_events[:10]:
            message += f"📅 {event['month']} {event['day']}\n"
            message += f"• {event['event']}\n"
            message += f"  📍 {event['country']} | {event['category']}\n\n"
        if len(found_events) > 10:
            message += f"... and {len(found_events) - 10} more events."
    else:
        message = f"🌍 **No events found for '{query}'**\n\nTry another country name."

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse events by category"""
    categories = {}
    for month_events in EVENTS.values():
        for event in month_events:
            cat = event["category"]
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

    message = "📚 **Browse by Category**\n\n"
    for cat, count in categories.items():
        message += f"• {cat} ({count} events)\n"

    message += "\nSend the category name to see events."

    await update.message.reply_text(message, parse_mode="Markdown")

async def handle_category_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category search from text input"""
    query = update.message.text.strip()
    
    found_events = []
    for month, month_events in EVENTS.items():
        for event in month_events:
            if query.lower() in event["category"].lower():
                found_events.append({
                    "month": month,
                    "event": event["event"],
                    "day": event["day"],
                    "country": event["country"],
                    "category": event["category"]
                })

    if found_events:
        message = f"📚 **Events in {query}**\n\n"
        for event in found_events[:10]:
            message += f"📅 {event['month']} {event['day']}\n"
            message += f"• {event['event']}\n"
            message += f"  📍 {event['country']}\n\n"
        if len(found_events) > 10:
            message += f"... and {len(found_events) - 10} more events."
    else:
        message = f"📚 **No events found for '{query}'**\n\nTry another category."

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to daily updates"""
    chat_id = update.effective_chat.id
    
    if chat_id not in subscribed_chats:
        subscribed_chats.append(chat_id)
        await update.message.reply_text(
            "✅ **Subscribed to daily updates!**\n\n"
            "You'll receive daily event notifications every morning.\n"
            "Use /unsubscribe to stop notifications."
        )
    else:
        await update.message.reply_text("ℹ️ You're already subscribed!")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from daily updates"""
    chat_id = update.effective_chat.id
    
    if chat_id in subscribed_chats:
        subscribed_chats.remove(chat_id)
        await update.message.reply_text("✅ **Unsubscribed from daily updates!**")
    else:
        await update.message.reply_text("ℹ️ You're not subscribed.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """❓ **Help - Anniversary Bot**

🗓️ **How to use:**

1️⃣ **Today's Events:**
   Use /today to see what's happening today

2️⃣ **Upcoming Events:**
   Use /upcoming to see events in the next 7 days

3️⃣ **Search by Country:**
   Use /country then type a country name

4️⃣ **Browse by Category:**
   Use /category then type a category

5️⃣ **Daily Updates:**
   Use /subscribe to get daily event notifications

📌 **Commands:**
/start - Welcome menu
/today - Events today
/upcoming - Events in 7 days
/country - Search by country
/category - Browse by category
/subscribe - Get daily updates
/unsubscribe - Stop updates
/help - This message

🌍 **Categories:** Political, Cultural, Historical, Holiday, Awareness
"""

    await update.message.reply_text(help_text, parse_mode="Markdown")

# ==================== CALLBACK HANDLERS ====================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "today_events":
        await today_command(update, context)
    
    elif query.data == "upcoming_events":
        await upcoming_command(update, context)
    
    elif query.data == "browse_country":
        await country_command(update, context)
    
    elif query.data == "subscribe":
        await subscribe_command(update, context)
    
    elif query.data == "help":
        await help_command(update, context)
    
    elif query.data == "back_to_menu":
        user = update.effective_user
        welcome_text = f"""🗓️ **Welcome back, {user.first_name}!**

What would you like to do?

📌 **Commands:**
/today - Events today
/upcoming - Events in 7 days
/country - Search by country
/category - Browse by category
"""
        keyboard = [
            [InlineKeyboardButton("📅 Today's Events", callback_data="today_events")],
            [InlineKeyboardButton("📆 Upcoming Events", callback_data="upcoming_events")],
            [InlineKeyboardButton("🌍 Browse by Country", callback_data="browse_country")],
            [InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# ==================== HELPER: Handle Text Input ====================
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for country/category search"""
    text = update.message.text.strip()
    
    # Check if it looks like a country search
    countries = set()
    for month_events in EVENTS.values():
        for event in month_events:
            countries.add(event["country"].lower())
    
    if text.lower() in countries:
        await handle_country_search(update, context)
        return
    
    # Check if it looks like a category search
    categories = set()
    for month_events in EVENTS.values():
        for event in month_events:
            categories.add(event["category"].lower())
    
    if any(text.lower() in cat for cat in categories):
        await handle_category_search(update, context)
        return
    
    # If not recognized, suggest commands
    await update.message.reply_text(
        "❓ **Command not recognized.**\n\n"
        "Try:\n"
        "• /today - Today's events\n"
        "• /upcoming - Upcoming events\n"
        "• /country - Search by country\n"
        "• /category - Browse by category\n"
        "• /help - All commands",
        parse_mode="Markdown"
    )

# ==================== AUTO-UPDATE JOB ====================
async def send_daily_updates(context: ContextTypes.DEFAULT_TYPE):
    """Send daily event updates to subscribers"""
    if not subscribed_chats:
        return

    today = datetime.now()
    month = today.strftime("%B")
    day = today.day

    events = EVENTS.get(month, [])
    today_events = [e for e in events if e["day"] == day]

    if today_events:
        message = f"📅 **Good Morning! Here are today's events - {today.strftime('%B %d, %Y')}**\n\n"
        for event in today_events:
            message += f"• {event['event']}\n"
            message += f"  📍 {event['country']} | {event['category']}\n\n"
        message += "Use /upcoming to see future events!"
    else:
        message = f"📅 **No major events today - {today.strftime('%B %d, %Y')}**\n\nCheck /upcoming for future events!"

    for chat_id in subscribed_chats:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown"
            )
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error sending to {chat_id}: {e}")

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ==================== MAIN ====================
async def main():
    """Start the bot"""
    logger.info("🗓️ Starting Anniversary Bot...")
    logger.info(f"📊 {len(EVENTS)} months of events loaded")

    # Create application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("upcoming", upcoming_command))
    application.add_handler(CommandHandler("country", country_command))
    application.add_handler(CommandHandler("category", category_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("help", help_command))

    # Handle text input for country/category search
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    # Add callback handler
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Add error handler
    application.add_error_handler(error_handler)

    # Setup job queue for daily updates
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_daily(
            send_daily_updates,
            time=datetime.strptime("08:00", "%H:%M").time(),
            name="daily_updates"
        )
        logger.info("⏰ Daily updates scheduled at 8:00 AM")
    else:
        logger.warning("⚠️ JobQueue not available - daily updates disabled")

    # Start the bot
    await application.initialize()
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("✅ Webhook removed, using polling mode")

    await application.start()
    await application.updater.start_polling()

    logger.info("✅ Anniversary Bot started successfully!")
    logger.info(f"👥 Subscribers: {len(subscribed_chats)}")
    logger.info("🤖 Bot is ready to receive messages")

    # Keep running
    while True:
        await asyncio.sleep(3600)
        logger.info(f"📊 Status: {len(subscribed_chats)} subscribers")

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
