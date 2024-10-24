# from apscheduler.schedulers.background import BackgroundScheduler
# from django.core.management import call_command

# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(run_check_eol, 'interval', seconds=30)  # Run every 30 seconds
#     scheduler.start()

# def run_check_eol():
#     call_command('check_eol')  # Runs the Django management command 'check_eol'


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.core.management import call_command

# Create a function to call the check_eol management command
def run_check_eol():
    call_command('check_eol')

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule the check_eol management command every 30 seconds
    scheduler.add_job(
        run_check_eol,  # Now using a serializable function reference
        trigger='interval',
        seconds=10,
        id='check_eol_job',
        max_instances=1,
        replace_existing=True
    )

    scheduler.start()
    print("Scheduler started.")

