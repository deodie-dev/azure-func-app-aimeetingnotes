import logging
import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */15 22-23,0-7 * * 1-5",
                   arg_name="myTimer",
                   run_on_startup=True,
                   use_monitor=False) 

def timer_trigger(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')

    from src.services.meeting_service import MeetingService
    from src.core.logger import setup_logger
    setup_logger()
    service = MeetingService()
    service.main()

    logging.info('Python timer trigger function executed.')


