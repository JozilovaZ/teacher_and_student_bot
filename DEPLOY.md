# Serverga deploy qilish

## 1. Serverga yuklash

### SCP orqali:
```bash
scp -r D:/BOT_DARSLARI/ustoz_shogirt_bot root@SERVER_IP:/root/
```

### Git orqali (tavsiya):
```bash
# Lokalda
git init && git add . && git commit -m "deploy"
git remote add origin https://github.com/USER/REPO.git
git push -u origin main

# Serverda
git clone https://github.com/USER/REPO.git
cd ustoz_shogirt_bot
```

---

## 2. Serverda sozlash

```bash
apt update && apt install python3 python3-pip python3-venv -y

cd /root/ustoz_shogirt_bot
python3 -m venv venv
venv/bin/pip install -r requirements.txt

cp .env.example .env
nano .env
```

### .env to'ldirish:
```
BOT_TOKEN=your_bot_token
ADMINS=your_telegram_id
ip=0.0.0.0
PORT=8006
WEBHOOK_HOST=https://your-domain.com
PROXY=
```

---

## 3. Nginx sozlash (webhook uchun)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /bot/ {
        proxy_pass http://127.0.0.1:8006;
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_set_header X-Real-IP \;
    }
}
```

```bash
# SSL (HTTPS) — webhook uchun majburiy
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## 4. Systemd service

```bash
cp ustoz_shogirt_bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ustoz_shogirt_bot
systemctl start ustoz_shogirt_bot
systemctl status ustoz_shogirt_bot
```

---

## 5. Loglar va boshqaruv

```bash
journalctl -u ustoz_shogirt_bot -f       # loglarni ko'rish
systemctl restart ustoz_shogirt_bot      # qayta ishga tushirish
systemctl stop ustoz_shogirt_bot         # to'xtatish
```

---

## Muhim eslatmalar

- WEBHOOK_HOST bo'sh bo'lsa — polling rejimida ishlaydi
- Webhook uchun HTTPS majburiy (Telegram talabi)
- PROXY= bo'sh qoldiring (serverda kerak emas)
- Database: utils/db_api/ustoz_shogirt.db serverda saqlanadi
- .env ni hech qachon git ga push qilmang
