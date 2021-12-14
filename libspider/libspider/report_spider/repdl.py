#!/usr/bin/python3
import sys
from libspider.report_spider.macro_report import event_record_macro_report, event_save_macro_report
from libspider.report_spider.stock_report import event_download_stock_report, event_save_stock_report
from libspider.report_spider.strategy_report import event_record_strategy_report, event_save_strategy_report
from libspider.report_spider.industry_report import event_record_industry_report, event_save_industry_report


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("python3 repdl n")
    else:
        if sys.argv[1].isdigit():
            days = int(sys.argv[1]) 
            event_record_industry_report(days)
            event_record_macro_report(days)
            event_record_strategy_report(days)
            event_download_stock_report(days)
            delta_time = 2
            event_save_industry_report(delta_time)
            event_save_macro_report(delta_time)
            event_save_strategy_report(delta_time)
            event_save_stock_report(delta_time)
