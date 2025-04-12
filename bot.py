import telebot, json, random, string, os
from vps_handler import run_task, add_vps, vps_status

# === BOT CONFIG ===
TOKEN = 'YOUR_BOT_TOKEN'  # Replace with BotFather token
bot = telebot.TeleBot(TOKEN)
SESSION = {}

# === CONFIG LOADING ===
with open("config.json") as f:
    config = json.load(f)
ADMIN_IDS = config["admins"]

# === ACCESS KEY STORAGE ===
def load_keys():
    try:
        with open("access_keys.json") as f:
            return json.load(f)
    except:
        return {}

def save_keys(data):
    with open("access_keys.json", "w") as f:
        json.dump(data, f)

# === COMMAND: /start ===
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    uid = str(msg.from_user.id)
    args = msg.text.split()
    if uid in SESSION:
        return send_welcome(msg, SESSION[uid])

    if len(args) == 2:
        key = args[1]
        keys = load_keys()
        if key in keys and not keys[key]["used"]:
            role = keys[key]["role"]
            SESSION[uid] = role
            keys[key]["used"] = True
            save_keys(keys)
            return send_welcome(msg, role)
    bot.reply_to(msg, "🔑 Please redeem a valid access key:\n/redeem <your-key>")

# === WELCOME SCREEN ===
def send_welcome(msg, role):
    banner = f"""
👋 Welcome to Mitra Drift Shell 🧠

You are verified as: {'🛡️ ADMIN' if role == 'admin' else '🟢 MEMBER'}

Available Commands:
/help – Show available commands
/imgb <ip> <port> <duration>
/status
{"\n/addvps <ip> <user> <pass>\n/genkey <role>" if role == 'admin' else ''}
"""
    bot.reply_to(msg, banner)

# === COMMAND: /genkey <member|admin> ===
@bot.message_handler(commands=['genkey'])
def genkey_cmd(msg):
    uid = str(msg.from_user.id)
    if SESSION.get(uid) != "admin":
        return bot.reply_to(msg, "⛔ Only admins can generate keys.")
    args = msg.text.split()
    if len(args) != 2 or args[1] not in ['admin', 'member']:
        return bot.reply_to(msg, "Usage: /genkey <member|admin>")
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    keys = load_keys()
    keys[key] = {"role": args[1], "used": False}
    save_keys(keys)
    bot.reply_to(msg, f"🔐 New {args[1].upper()} key:\n`{key}`", parse_mode="Markdown")

# === COMMAND: /redeem <key> ===
@bot.message_handler(commands=['redeem'])
def redeem_cmd(msg):
    uid = str(msg.from_user.id)
    args = msg.text.split()
    if len(args) != 2:
        return bot.reply_to(msg, "Usage: /redeem <key>")
    key = args[1]
    keys = load_keys()
    if key in keys and not keys[key]["used"]:
        role = keys[key]["role"]
        SESSION[uid] = role
        keys[key]["used"] = True
        save_keys(keys)
        return send_welcome(msg, role)
    else:
        return bot.reply_to(msg, "❌ Invalid or used key.")

# === COMMAND: /help ===
@bot.message_handler(commands=['help'])
def help_cmd(msg):
    uid = str(msg.from_user.id)
    role = SESSION.get(uid)
    if not role:
        return bot.reply_to(msg, "Please redeem an access key first.")
    cmds = [
        "/imgb <ip> <port> <duration>",
        "/status"
    ]
    if role == "admin":
        cmds += ["/addvps <ip> <user> <pass>", "/genkey <role>"]
    bot.reply_to(msg, "📘 Available Commands:\n" + "\n".join(cmds))

# === COMMAND: /addvps ===
@bot.message_handler(commands=['addvps'])
def add_vps_cmd(msg):
    if SESSION.get(str(msg.from_user.id)) != "admin":
        return bot.reply_to(msg, "⛔ Admin only.")
    args = msg.text.split()
    if len(args) != 4:
        return bot.reply_to(msg, "Usage: /addvps <ip> <user> <pass>")
    ip, user, pw = args[1:]
    add_vps(ip, user, pw)
    bot.reply_to(msg, f"✅ VPS {ip} added.")

# === COMMAND: /imgb ===
@bot.message_handler(commands=['imgb'])
def imgb_cmd(msg):
    if str(msg.from_user.id) not in SESSION:
        return bot.reply_to(msg, "Please redeem a key first.")
    args = msg.text.split()
    if len(args) != 4:
        return bot.reply_to(msg, "Usage: /imgb <ip> <port> <duration>")
    ip, port, dur = args[1:]
    out = run_task(ip, port, dur)
    bot.reply_to(msg, f"🚀 Started on {out} VPS.")

# === /status ===
@bot.message_handler(commands=['status'])
def status_cmd(msg):
    if str(msg.from_user.id) not in SESSION:
        return bot.reply_to(msg, "Please redeem a key first.")
    out = vps_status()
    bot.reply_to(msg, out)

bot.polling()
