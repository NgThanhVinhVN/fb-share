import requests, random, string, datetime, pytz, threading, time, os

def load_user_agents():
    if os.path.exists("useragent.txt"):
        with open("useragent.txt", "r", encoding="utf-8") as f:
            uas = [line.strip() for line in f if line.strip()]
            if uas: return uas
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/128.0",
    ]

USER_AGENTS = load_user_agents()

def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def log(message, thread_id=None):
    timestamp = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%H:%M:%S")
    prefix = f"[Luồng {thread_id}]" if thread_id else ""
    print(f"[{timestamp}] {prefix} {message}")

def share_loop(tokens, post_id, privacy, total, delay, thread_id):
    headers = {"accept": "application/json"}
    success, failed, number = 0, 0, 1
    while (success + failed) < total:
        token = tokens[(number - 1) % len(tokens)]
        headers["User-Agent"] = random.choice(USER_AGENTS)
        link = f"https://m.facebook.com/{post_id}?rnd={random_string()}"
        status = f"{random_string(6)}"
        url = "https://graph.facebook.com/me/feed"
        params = {
            "link": link,
            "message": status,
            "published": "0",
            "privacy": f'{{"value":"{privacy}"}}',
            "access_token": token
        }
        try:
            r = requests.post(url, headers=headers, data=params, timeout=15)
            if "id" in r.text:
                success += 1
                log(f"[{number}] SUCCESS || {r.json()['id']}", thread_id)
            else:
                failed += 1
                log(f"[X] FAIL || Token:{token[:15]}... || {r.text[:60]}", thread_id)
        except Exception as e:
            failed += 1
            log(f"[X] EXC || {str(e)}", thread_id)
        number += 1
        time.sleep(delay + random.uniform(0.8, 2.5))
    log(f"[DONE] SUCCESS: {success} || ERROR: {failed}", thread_id)

if __name__ == "__main__":
    post_id = input("Post ID: ").strip()
    delay = int(input("Delay (ms): ").strip()) / 1000.0
    total = int(input("Tổng share mỗi luồng: ").strip())
    threads = int(input("Số threads: ").strip())
    privacy = input("Privacy (SELF/EVERYONE): ").strip().upper()

    tokens = []
    if os.path.exists("token.txt"):
        with open("token.txt", "r", encoding="utf-8") as f:
            tokens = [line.strip() for line in f if line.strip()]

    if not tokens:
        print("Chưa có token, mời nhập (nhiều token cách nhau bằng dấu phẩy):")
        input_tokens = input("Tokens: ").strip()
        tokens = [t.strip() for t in input_tokens.split(",") if t.strip()]
        with open("token.txt", "w", encoding="utf-8") as f:
            for t in tokens:
                f.write(t + "\n")

    if not tokens:
        print("Không có token!"); exit()

    log(f"Start | Threads={threads} | Delay={delay}s | Total={total} | Tokens={len(tokens)}")
    ths = []
    for i in range(threads):
        t = threading.Thread(target=share_loop, args=(tokens, post_id, privacy, total, delay, i+1), daemon=True)
        ths.append(t); t.start()
    for t in ths: t.join()
    log("Hoàn tất.")
