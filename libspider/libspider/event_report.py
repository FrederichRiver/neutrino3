#!/usr/bin/python38
from libspider.macro_report import event_record_macro_report, event_save_macro_report
from libspider.stock_report import event_download_stock_report, event_save_stock_report
from libspider.strategy_report import event_record_strategy_report, event_save_strategy_report
from libspider.industry_report import event_record_industry_report, event_save_industry_report


def event_record_report():
    #event_record_industry_report(3)
    #event_record_macro_report(3)
    #event_record_strategy_report(3)
    #event_download_stock_report(3)
    event_save_industry_report(1)
    #event_save_macro_report(2)
    #event_save_strategy_report(2)
    #event_save_stock_report(2)


event_record_report()
