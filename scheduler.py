from apscheduler.schedulers.blocking import BlockingScheduler
from bot import buy_tokens, sell_tokens

def timed_job():
    print("satın alma...")
    buy_tokens()
    print("satma...")
    sell_tokens()
    print("Zamanlanmış iş tamamlandı.")

scheduler = BlockingScheduler()

scheduler.add_job(timed_job, 'interval', minutes=15)

print("Scheduler başlatılıyor...")
scheduler.start()
