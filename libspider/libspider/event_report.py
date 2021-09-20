#!/usr/bin/python38
from libspider.macro_report import event_record_macro_report, event_save_macro_report
from libspider.stock_report import event_download_stock_report, event_save_stock_report
from libspider.strategy_report import event_record_strategy_report, event_save_strategy_report
from libspider.industry_report import event_record_industry_report, event_save_industry_report


def event_record_report():
    days = 2
    event_record_industry_report(days)
    event_record_macro_report(days)
    event_record_strategy_report(days)
    event_download_stock_report(days)
    delta_time = 2
    event_save_industry_report(delta_time)
    event_save_macro_report(delta_time)
    event_save_strategy_report(delta_time)
    event_save_stock_report(delta_time)


event_record_report()
