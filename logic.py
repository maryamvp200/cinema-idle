import os
import time
import json
import sys

SAVE_FILE = "cinema_save.json"

# ==================== وضعیت بازی ====================
state = {
    "money": 0,
    "total_earned": 0,
    "halls": [
        {"level": 1, "unlocked": True,  "cost": 0},
        {"level": 0, "unlocked": False, "cost": 100},
        {"level": 0, "unlocked": False, "cost": 1000}
    ],
    "toilet":  {"level": 1, "unlocked": True, "cost": 0},
    "station": {"level": 1, "unlocked": True, "cost": 0},
    "employees": {
        "ticket_seller":  {"level": 0, "cost": 50, "multiplier": 0.1},
        "popcorn_seller": {"level": 0, "cost": 75, "multiplier": 0.1},
        "cleaner":        {"level": 0, "cost": 60, "multiplier": 0.05}
    },
    "prestige": 1.0
}

# ==================== توابع کمکی ====================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_income():
    inc = 0.0
    for h in state["halls"]:
        if h["unlocked"]:
            inc += h["level"] * 1.0
    if state["toilet"]["unlocked"]:
        inc += state["toilet"]["level"] * 2.0
    if state["station"]["unlocked"]:
        inc += state["station"]["level"] * 3.0
    base = inc
    for emp in state["employees"].values():
        inc += base * emp["level"] * emp["multiplier"]
    inc *= state["prestige"]
    return int(inc)

def save():
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f)

def load():
    global state
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            state = json.load(f)

def format_money(n):
    return f"{n:,}"

def draw_ui():
    clear()
    income = calculate_income()
    print("╔══════════════════════════════════════════════╗")
    print("║           🎬 CINEMA IDLE 🎬                  ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  💰 پول: {format_money(state['money']):<35}║")
    print(f"║  ⭐ درآمد: {income}/ثانیه{'':<27}║")
    print(f"║  🏆 کل: {format_money(state['total_earned']):<37}║")
    print("╠══════════════════════════════════════════════╣")
    print("║  سالن‌ها:                                     ║")
    for i, h in enumerate(state["halls"]):
        if h["unlocked"]:
            line = f"║  [{i+1}] سالن {i+1}  (سطح {h['level']})  درآمد: {h['level']}/s  ✅"
        else:
            line = f"║  [{i+1}] سالن {i+1}  🔒 قفل  ({h['cost']} سکه)"
        print(line + " " * (46 - len(line)) + "║")
    print(f"║  [4] 🚻 دستشویی  (سطح {state['toilet']['level']})" + " " * 20 + "║")
    print(f"║  [5] 🎫 ایستگاه  (سطح {state['station']['level']})" + " " * 20 + "║")
    print("╠══════════════════════════════════════════════╣")
    print("║  کارمندها:                                   ║")
    for name, emp in state["employees"].items():
        print(f"║  [{name}] سطح {emp['level']}  (هزینه: {emp['cost']})" + " " * 15 + "║")
    print("╠══════════════════════════════════════════════╣")
    print("║  [U] ارتقاء  [B] خرید  [S] ذخیره  [Q] خروج   ║")
    print("╚══════════════════════════════════════════════╝")

# ==================== عمل‌ها ====================
def upgrade_hall(idx):
    h = state["halls"][idx]
    if not h["unlocked"]:
        return "❌ این سالن قفله!"
    cost = int(50 * (h["level"] ** 1.5))
    if state["money"] >= cost:
        state["money"] -= cost
        h["level"] += 1
        return f"✅ سالن {idx+1} به سطح {h['level']} ارتقاء یافت! (هزینه: {cost})"
    return f"❌ پول کافی نداری! نیاز: {cost}"

def unlock_hall(idx):
    h = state["halls"][idx]
    if h["unlocked"]:
        return "❌ این سالن قبلاً باز شده!"
    if state["money"] >= h["cost"]:
        state["money"] -= h["cost"]
        h["unlocked"] = True
        h["level"] = 1
        return f"✅ سالن {idx+1} باز شد!"
    return f"❌ پول کافی نداری! نیاز: {h['cost']}"

def upgrade_toilet():
    t = state["toilet"]
    cost = int(30 * (t["level"] ** 1.5))
    if state["money"] >= cost:
        state["money"] -= cost
        t["level"] += 1
        return f"✅ دستشویی به سطح {t['level']} ارتقاء یافت! (هزینه: {cost})"
    return f"❌ پول کافی نداری! نیاز: {cost}"

def upgrade_station():
    s = state["station"]
    cost = int(40 * (s["level"] ** 1.5))
    if state["money"] >= cost:
        state["money"] -= cost
        s["level"] += 1
        return f"✅ ایستگاه به سطح {s['level']} ارتقاء یافت! (هزینه: {cost})"
    return f"❌ پول کافی نداری! نیاز: {cost}"

def hire_employee(name):
    emp = state["employees"][name]
    if state["money"] >= emp["cost"]:
        state["money"] -= emp["cost"]
        emp["level"] += 1
        emp["cost"] = int(emp["cost"] * 1.5)
        return f"✅ {name} استخدام شد! (سطح {emp['level']})"
    return f"❌ پول کافی نداری! نیاز: {emp['cost']}"

# ==================== حلقه‌ی اصلی ====================
def main():
    load()
    last_tick = time.time()
    last_draw = 0

    while True:
        now = time.time()
        # درآمد هر ثانیه
        if now - last_tick >= 1.0:
            income = calculate_income()
            state["money"] += income
            state["total_earned"] += income
            last_tick = now

        # رسم UI هر ۱ ثانیه
        if now - last_draw >= 1.0:
            draw_ui()
            last_draw = now
            print("\n>> ", end="", flush=True)

        # ورودی غیرمسدود
        if sys.stdin in [sys.stdin]:
            import select
            # فقط در ویندوز: از msvcrt استفاده می‌کنیم
            if os.name == 'nt':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    print(key)
                    if key == 'q':
                        save()
                        print("👋 ذخیره شد. خروج.")
                        break
                    elif key == 's':
                        save()
                        print("💾 ذخیره شد!")
                    elif key == '1':
                        print(upgrade_hall(0) if state["halls"][0]["unlocked"] else unlock_hall(0))
                    elif key == '2':
                        print(upgrade_hall(1) if state["halls"][1]["unlocked"] else unlock_hall(1))
                    elif key == '3':
                        print(upgrade_hall(2) if state["halls"][2]["unlocked"] else unlock_hall(2))
                    elif key == '4':
                        print(upgrade_toilet())
                    elif key == '5':
                        print(upgrade_station())
                    elif key == 't':
                        print(hire_employee("ticket_seller"))
                    elif key == 'p':
                        print(hire_employee("popcorn_seller"))
                    elif key == 'c':
                        print(hire_employee("cleaner"))
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        save()
        print("\n👋 ذخیره شد.")