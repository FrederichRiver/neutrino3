#!/usr/bin/python3
from sqlalchemy import Column, String, Integer, Float, Date, BLOB
from sqlalchemy.ext.declarative import declarative_base


__version__ = (1, 0, 13)

# Form:
# 1.Company_info
# 2.Company_stock_structure
# 3.

Base = declarative_base()


class announce_manager(Base):
    __tablename__ = 'announce_manager'
    announce_id = Column(String(12), primary_key=True)
    stock_code = Column(String(10))
    title = Column(BLOB())
    announce_timestamp = Column(Integer)
    url = Column(String(100))
    announce_type = Column(String(20))


class company_info(Base):
    __tablename__ = 'company_info'
    # index = Column(Integer, nullable=False, autoincrement=True)
    company_name = Column(String(100))
    english_name = Column(String(100))
    stock_code = Column(String(10), primary_key=True)
    # type: 1,state enterprise; 2,
    # type = Column(Integer)
    legal_representative = Column(String(20))
    address = Column(String(100))
    chairman = Column(String(20))
    secratery = Column(String(20))
    main_business = Column(String(100))
    business_scope = Column(String(1000))
    introduction = Column(String(1000))


class company_stock_structure(Base):
    __tablename__ = 'company_stock_structure'
    stock_code = Column(String(10), primary_key=True)
    stock_name = Column(String(10))
    report_date = Column(Date, primary_key=True)
    total_stock = Column(Float)


class formInterest(Base):
    """
    This is the template of stock interest.
    """
    __tablename__ = 'stock_interest'
    report_date = Column(Date, primary_key=True)
    char_stock_code = Column(String(10), primary_key=True)
    int_year = Column(Integer)
    float_bonus = Column(Float)
    float_increase = Column(Float)
    float_dividend = Column(Float)
    record_date = Column(Date)
    xrdr_date = Column(Date)
    share_date = Column(Date)


class formShibor(Base):
    __tablename__ = 'shibor'
    release_date = Column(Date, primary_key=True)
    overnight = Column(Float)
    one_week = Column(Float)
    two_week = Column(Float)
    one_month = Column(Float)
    three_month = Column(Float)
    six_month = Column(Float)
    nine_month = Column(Float)
    one_year = Column(Float)


class formStockManager(Base):
    __tablename__ = 'stock_manager'
    stock_code = Column(String(10), primary_key=True)
    stock_name = Column(String(20))
    orgId = Column(String(25))
    short_code = Column(String(10))
    create_date = Column(Date)
    update_date = Column(Date)
    xrdr_date = Column(Date)
    balance_date = Column(Date)
    income_date = Column(Date)
    cashflow_date = Column(Date)
    flag = Column(String(10))

    def __str__(self):
        return "<Stock Manager>"


class formUSStockManager(Base):
    __tablename__ = 'us_stock_manager'
    stock_code = Column(String(10), primary_key=True)
    stock_name = Column(String(20))

    def __str__(self):
        return "<US Stock Manager>"


formStockManager_column = [
    "stock_code", "stock_name", "orgId", "short_code", "create_date", "modified_date",
    "xrdr_date", "balance_date", "income_date", "cashflow_date", "flag"
]


class formStock(Base):
    __tablename__ = 'template_stock'
    trade_date = Column(Date, primary_key=True)
    stock_name = Column(String(20))
    close_price = Column(Float, default=0)
    high_price = Column(Float, default=0)
    low_price = Column(Float, default=0)
    open_price = Column(Float, default=0)
    prev_close_price = Column(Float, default=0)
    change_rate = Column(Float, default=0)
    amplitude = Column(Float, default=0)
    volume = Column(Integer, default=0)
    turnover = Column(Float, default=0)
    adjust_factor = Column(Float, default=1)

    def __str__(self):
        return "<Stock template>"


formStock_column = [
    'trade_date', 'stock_code', 'stock_name', 'close_price', 'high_price',
    'low_price', 'open_price', 'prev_close_price', 'change_rate', 'amplitude',
    'volume', 'turnover', 'adjust_factor']


class formBalance(Base):
    __tablename__ = 'balance_sheet'
    report_date = Column(Date, primary_key=True)
    char_stock_code = Column(String(10), primary_key=True)
    float_assets = Column(Float, comment='assets')
    float_c1_current_assets = Column(Float, comment='current assets')
    float_c1_1 = Column(Float, comment='bank and cash')
    float_c1_2 = Column(Float, comment='provision_of_settlement_fund')
    float_c1_3 = Column(Float, comment='lent_fund')
    float_c1_4 = Column(Float, comment='financial_asset_held_for_trading')
    float_c1_5 = Column(Float, comment='derivative_financial_asset')
    float_c1_6 = Column(Float, comment='notes_receivable')
    float_c1_7 = Column(Float, comment='accounts_receivable')
    float_c1_8 = Column(Float, comment='prepayment')
    float_c1_9 = Column(Float, comment='insurance_premiums_receivable')
    float_c1_10 = Column(Float, comment='cession_premiums_receivable')
    float_c1_11 = Column(Float, comment='provision_of_cession_receivable')
    float_c1_12 = Column(Float, comment='interest_receivable')
    float_c1_13 = Column(Float, comment='dividend_receivable')
    float_c1_14 = Column(Float, comment='other_receivable')
    float_c1_15 = Column(Float, comment='export_drawback_receivable')
    float_c1_16 = Column(Float, comment='allowance_receivable')
    float_c1_17 = Column(Float, comment='deposite_recievable')
    float_c1_18 = Column(Float, comment='internal_recievables')
    float_c1_19 = Column(Float, comment='recoursable_financial_assets_acquired')
    float_c1_20 = Column(Float, comment='inventory')
    float_c1_21 = Column(Float, comment='deferred_expense')
    float_c1_22 = Column(Float, comment='unsettled_gross_and_loss_on_current_asset')
    float_c1_23 = Column(Float, comment='long_term_debenture_investment_falling_due_in_a_year')
    float_c1_24 = Column(Float, comment='other_current_asset')
    float_c2_non_current_assets = Column(Float, comment='non_current_assets')
    float_c2_1 = Column(Float, comment='loans_and_payments_on_behalf')
    float_c2_2 = Column(Float, comment='financial_asset_available_for_sale')
    float_c2_3 = Column(Float, comment='investment_held_to_maturity')
    float_c2_4 = Column(Float, comment='long_term_receivable')
    float_c2_5 = Column(Float, comment='long_term_equity_investment')
    float_c2_6 = Column(Float, comment='other_long_term_investment')
    float_c2_7 = Column(Float, comment='investment_real_estate')
    float_c2_8 = Column(Float, comment='fixed_asset_original_cost')
    float_c2_9 = Column(Float, comment='accmulated_depreciation')
    float_c2_10 = Column(Float, comment='fixed_asset_net_value')
    float_c2_11 = Column(Float, comment='provision_of_fixed_asset_impairment')
    float_c2_12 = Column(Float, comment='fixed_asset')
    float_c2_13 = Column(Float, comment='construction_in_progress')
    float_c2_14 = Column(Float, comment='construction_supplies')
    float_c2_15 = Column(Float, comment='fixed_asset_pending_disposal')
    float_c2_16 = Column(Float, comment='bearer_bio_asset')
    float_c2_17 = Column(Float, comment='bio_asset')
    float_c2_18 = Column(Float, comment='oil_and_gas_asset')
    float_c2_19 = Column(Float, comment='intangible_asset')
    float_c2_20 = Column(Float, comment='rd_cost')
    float_c2_21 = Column(Float, comment='goodwill')
    float_c2_22 = Column(Float, comment='long_term_deferred_expense')
    float_c2_23 = Column(Float, comment='circulation_right_for_equity_separation')
    float_c2_24 = Column(Float, comment='deferred_tax_asset')
    float_c2_25 = Column(Float, comment='other_non_current_asset')
    float_liability = Column(Float, comment='liability')
    float_c3_current_liability = Column(Float, comment='current_liability')
    float_c3_1 = Column(Float, comment='short_term_loan')
    float_c3_2 = Column(Float, comment='loan_from_central_bank')
    float_c3_3 = Column(Float, comment='deposite_from_customer_and_interbank')
    float_c3_4 = Column(Float, comment='deposite_fund')
    float_c3_5 = Column(Float, comment='financial_liability_held_for_trading')
    float_c3_6 = Column(Float, comment='derivative_financial_liability')
    float_c3_7 = Column(Float, comment='note_payable')
    float_c3_8 = Column(Float, comment='accout_payable')
    float_c3_9 = Column(Float, comment='advance_from_customer')
    float_c3_10 = Column(Float, comment='fund_from_sale_of_financial_asset_with_repurchasement_agreement')
    float_c3_11 = Column(Float, comment='handling_charge_and_commission_payable')
    float_c3_12 = Column(Float, comment='employee_benefit_payable')
    float_c3_13 = Column(Float, comment='tax_payable')
    float_c3_14 = Column(Float, comment='interest_payable')
    float_c3_15 = Column(Float, comment='dividend_payable')
    float_c3_16 = Column(Float, comment='other_payable')
    float_c3_17 = Column(Float, comment='cession_insurance_payable')
    float_c3_18 = Column(Float, comment='internal_payable')
    float_c3_19 = Column(Float, comment='other_payable')
    float_c3_20 = Column(Float, comment='provision_for_expense')
    float_c3_21 = Column(Float, comment='accured_liability')
    float_c3_22 = Column(Float, comment='account_payable_reinsurance')
    float_c3_23 = Column(Float, comment='reserve_for_insurance_contract')
    float_c3_24 = Column(Float, comment='acting_trading_security')
    float_c3_25 = Column(Float, comment='acting_underwriting_security')
    float_c3_26 = Column(Float, comment='international_bill_settlement')
    float_c3_27 = Column(Float, comment='domestic_bill_settlement')
    float_c3_28 = Column(Float, comment='deferred_income')
    float_c3_29 = Column(Float, comment='short_term_bonds_payable')
    float_c3_30 = Column(Float, comment='none_current_liability_due_within_one_year')
    float_c3_31 = Column(Float, comment='other_none_current_liability')
    float_c4_long_term_liability = Column(Float, comment='long_term_liability')
    float_c4_1 = Column(Float, comment='long_term_loan')
    float_c4_2 = Column(Float, comment='bonds_payable')
    float_c4_3 = Column(Float, comment='long_term_payable')
    float_c4_4 = Column(Float, comment='specific_payable')
    float_c4_5 = Column(Float, comment='estimated_none_current_liability')
    float_c4_6 = Column(Float, comment='long_term_deferred_income')
    float_c4_7 = Column(Float, comment='deferred_tax_liability')
    float_c4_8 = Column(Float, comment='other_none_current_liability')
    float_owner_equity = Column(Float, comment='owner_equity')
    float_c6_equity_attributable_to_parent_company = Column(Float, comment='equity_attributable_to_parent_company')
    float_c6_1 = Column(Float, comment='paid_up_capital')
    float_c6_2 = Column(Float, comment='capital_surplus')
    float_c6_3 = Column(Float, comment='treasury_stock')
    float_c6_4 = Column(Float, comment='specific_reserve')
    float_c6_5 = Column(Float, comment='surplus_reserve')
    float_c6_6 = Column(Float, comment='general_risk_preperation')
    float_c6_7 = Column(Float, comment='unaffirmed_investment_loss')
    float_c6_8 = Column(Float, comment='retained_earning')
    float_c6_9 = Column(Float, comment='cash_dividend_to_be_distributed')
    float_c6_10 = Column(Float, comment='converted_difference_in_foreign_currency_statements')
    float_c7_minority_interest = Column(Float, comment='minority_interest')
    float_liability_and_equity = Column(Float, comment='liability_and_equity')


balance_column = [
    'float_c1_1',
    'float_c1_2',
    'float_c1_3',
    'float_c1_4',
    'float_c1_5',
    'float_c1_6',
    'float_c1_7',
    'float_c1_8',
    'float_c1_9',
    'float_c1_10',
    'float_c1_11',
    'float_c1_12',
    'float_c1_13',
    'float_c1_14',
    'float_c1_15',
    'float_c1_16',
    'float_c1_17',
    'float_c1_18',
    'float_c1_19',
    'float_c1_20',
    'float_c1_21',
    'float_c1_22',
    'float_c1_23',
    'float_c1_24',
    'float_c1_current_assets',
    'float_c2_1',
    'float_c2_2',
    'float_c2_3',
    'float_c2_4',
    'float_c2_5',
    'float_c2_6',
    'float_c2_7',
    'float_c2_8',
    'float_c2_9',
    'float_c2_10',
    'float_c2_11',
    'float_c2_12',
    'float_c2_13',
    'float_c2_14',
    'float_c2_15',
    'float_c2_16',
    'float_c2_17',
    'float_c2_18',
    'float_c2_19',
    'float_c2_20',
    'float_c2_21',
    'float_c2_22',
    'float_c2_23',
    'float_c2_24',
    'float_c2_25',
    'float_c2_non_current_assets',
    'float_assets',
    'float_c3_1',
    'float_c3_2',
    'float_c3_3',
    'float_c3_4',
    'float_c3_5',
    'float_c3_6',
    'float_c3_7',
    'float_c3_8',
    'float_c3_9',
    'float_c3_10',
    'float_c3_11',
    'float_c3_12',
    'float_c3_13',
    'float_c3_14',
    'float_c3_15',
    'float_c3_16',
    'float_c3_17',
    'float_c3_18',
    'float_c3_19',
    'float_c3_20',
    'float_c3_21',
    'float_c3_22',
    'float_c3_23',
    'float_c3_24',
    'float_c3_25',
    'float_c3_26',
    'float_c3_27',
    'float_c3_28',
    'float_c3_29',
    'float_c3_30',
    'float_c3_31',
    'float_c3_current_liability',
    'float_c4_1',
    'float_c4_2',
    'float_c4_3',
    'float_c4_4',
    'float_c4_5',
    'float_c4_6',
    'float_c4_7',
    'float_c4_8',
    'float_c4_long_term_liability',
    'float_liability',
    'float_c6_1',
    'float_c6_2',
    'float_c6_3',
    'float_c6_4',
    'float_c6_5',
    'float_c6_6',
    'float_c6_7',
    'float_c6_8',
    'float_c6_9',
    'float_c6_10',
    'float_c6_equity_attributable_to_parent_company',
    'float_c7_minority_interest',
    'float_owner_equity',
    'float_liability_and_equity'
]


class formIncomeStatement(Base):
    __tablename__ = 'income_statement'
    report_date = Column(Date, primary_key=True)
    char_stock_code = Column(String(10), primary_key=True)
    float_c1 = Column(Float, comment='total_revenue')
    float_c2 = Column(Float, comment='revenue')
    float_c3 = Column(Float, comment='interest_income')
    float_c4 = Column(Float, comment='')
    float_c5 = Column(Float, comment='')
    float_c6 = Column(Float, comment='')
    float_c7 = Column(Float, comment='')
    float_c8 = Column(Float, comment='')
    float_c9 = Column(Float, comment='')
    float_c10 = Column(Float, comment='')
    float_c11 = Column(Float, comment='')
    float_c12 = Column(Float, comment='')
    float_c13 = Column(Float, comment='rd expense')
    float_c14 = Column(Float, comment='')
    float_c15 = Column(Float, comment='')
    float_c16 = Column(Float, comment='')
    float_c17 = Column(Float, comment='')
    float_c18 = Column(Float, comment='')
    float_c19 = Column(Float, comment='')
    float_c20 = Column(Float, comment='')
    float_c21 = Column(Float, comment='')
    float_c22 = Column(Float, comment='')
    float_c23 = Column(Float, comment='')
    float_c24 = Column(Float, comment='financial expense')
    float_c25 = Column(Float, comment='')
    float_c26 = Column(Float, comment='investment income')
    float_c27 = Column(Float, comment='')
    float_c28 = Column(Float, comment='')
    float_c29 = Column(Float, comment='')
    float_c30 = Column(Float, comment='')
    float_c31 = Column(Float, comment='')
    float_c32 = Column(Float, comment='')
    float_c33 = Column(Float, comment='')
    float_c34 = Column(Float, comment='')
    float_c35 = Column(Float, comment='')
    float_c36 = Column(Float, comment='')
    float_c37 = Column(Float, comment='total profit')
    float_c38 = Column(Float, comment='')
    float_c39 = Column(Float, comment='income tax')
    float_c40 = Column(Float, comment='')
    float_c41 = Column(Float, comment='net profit')
    float_c42 = Column(Float, comment='')
    float_c43 = Column(Float, comment='minority interest')
    float_c44 = Column(Float, comment='')
    float_c45 = Column(Float, comment='')


income_column = [f"float_c{i+1}" for i in range(45)]


"""
class formIncomeStatement(formFinanceTemplate):
    __tablename__ = 'income_statement'
    report_period = Column(Date, primary_key=True)
    r1_revenue = Column(Float, comment='')
    r2_less_cost_of_sales = Column(Float, comment='')
    r3_sales_tax = Column(Float)
    r4_gross_profit = Column(Float)
    r5_add_other_operating_income = Column(Float)
    r6_less_other_operating_expense = Column(Float)
    r7_less_selling_and_distribution_expense = Column(Float)
    r8_g_a_expense = Column(Float)
    r9_finance_expense = Column(Float)
    r10_profit_from_operation = Column(Float)
    r12_subsidy_income = Column(Float)
    r13_non_operating_income = Column(Float)
    r14_less_non_operating_expense = Column(Float)
    r15_profit_before_tax = Column(Float)
    r16_less_income_tax = Column(Float)
    r17_ = Column(Float)
    r18_add_unrealised_investment_losses = Column(Float)
    r20_add_retained_profit = Column(Float)
    r21_other_transfer_in = Column(Float)
    r22_profit_available_for_distribution = Column(Float)
    r23_less_appropriation_of_statutory_surplus_reserves = Column(Float)
    r24_appropriation_of_statutory_welfare_fund = Column(Float)
    r25_appropriation_of_staff_incentive_and_welfare_fund = Column(Float)
    r26_appropriation_of_reserve_fund = Column(Float)
    r27_appropriation_of_enterprise_expansion_fund = Column(Float)
    r28_captial_redemption = Column(Float)
    r29_profit_avaliable_for_owners_distribution = Column(Float)
    r30_less_appropriation_of_preference_share_dividend = Column(Float)
    r31_appropriation_of_discretionary_surplus_reserve = Column(Float)
    r32_appropriation_of_ordinary_share_dividend = Column(Float)
    r33_transfer_from_ordinary_share_dividend_to_paid_in_capital = Column(Float)
    r34_retained_profit_after_appropriation = Column(Float)
    r35_supplementary_infomation = Column(Float)
"""


class formCashFlow(Base):
    __tablename__ = 'cashflow'
    report_date = Column(Date, primary_key=True)
    char_stock_code = Column(String(10), primary_key=True)
    float_c1 = Column(Float, comment='')
    float_c2 = Column(Float, comment='')
    float_c3 = Column(Float, comment='')
    float_c4 = Column(Float, comment='')
    float_c5 = Column(Float, comment='')
    float_c6 = Column(Float, comment='')
    float_c7 = Column(Float, comment='')
    float_c8 = Column(Float, comment='')
    float_c9 = Column(Float, comment='')
    float_c10 = Column(Float, comment='')
    float_c11 = Column(Float, comment='')
    float_c12 = Column(Float, comment='')
    float_c13 = Column(Float, comment='')
    float_c14 = Column(Float, comment='')
    float_c15 = Column(Float, comment='')
    float_c16 = Column(Float, comment='')
    float_c17 = Column(Float, comment='')
    float_c18 = Column(Float, comment='')
    float_c19 = Column(Float, comment='')
    float_c20 = Column(Float, comment='')
    float_c21 = Column(Float, comment='')
    float_c22 = Column(Float, comment='')
    float_c23 = Column(Float, comment='')
    float_c24 = Column(Float, comment='')
    float_c25 = Column(Float, comment='')
    float_c26 = Column(Float, comment='')
    float_c27 = Column(Float, comment='')
    float_c28 = Column(Float, comment='')
    float_c29 = Column(Float, comment='')
    float_c30 = Column(Float, comment='')
    float_c31 = Column(Float, comment='')
    float_c32 = Column(Float, comment='')
    float_c33 = Column(Float, comment='')
    float_c34 = Column(Float, comment='')
    float_c35 = Column(Float, comment='')
    float_c36 = Column(Float, comment='')
    float_c37 = Column(Float, comment='')
    float_c38 = Column(Float, comment='')
    float_c39 = Column(Float, comment='')
    float_c40 = Column(Float, comment='')
    float_c41 = Column(Float, comment='')
    float_c42 = Column(Float, comment='')
    float_c43 = Column(Float, comment='')
    float_c44 = Column(Float, comment='')
    float_c45 = Column(Float, comment='')
    float_c46 = Column(Float, comment='')
    float_c47 = Column(Float, comment='')
    float_c48 = Column(Float, comment='')
    float_c49 = Column(Float, comment='')
    float_c50 = Column(Float, comment='')
    float_c51 = Column(Float, comment='')
    float_c52 = Column(Float, comment='')
    float_c53 = Column(Float, comment='')
    float_c54 = Column(Float, comment='')
    float_c55 = Column(Float, comment='')
    float_c56 = Column(Float, comment='')
    float_c57 = Column(Float, comment='')
    float_c58 = Column(Float, comment='')
    float_c59 = Column(Float, comment='')
    float_c60 = Column(Float, comment='')
    float_c61 = Column(Float, comment='')
    float_c62 = Column(Float, comment='')
    float_c63 = Column(Float, comment='')
    float_c64 = Column(Float, comment='')
    float_c65 = Column(Float, comment='')
    float_c66 = Column(Float, comment='')
    float_c67 = Column(Float, comment='')
    float_c68 = Column(Float, comment='')
    float_c69 = Column(Float, comment='')
    float_c70 = Column(Float, comment='')
    float_c71 = Column(Float, comment='')
    float_c72 = Column(Float, comment='')
    float_c73 = Column(Float, comment='')
    float_c74 = Column(Float, comment='')
    float_c75 = Column(Float, comment='')
    float_c76 = Column(Float, comment='')
    float_c77 = Column(Float, comment='')
    float_c78 = Column(Float, comment='')
    float_c79 = Column(Float, comment='')
    float_c80 = Column(Float, comment='')
    float_c81 = Column(Float, comment='')
    float_c82 = Column(Float, comment='')
    float_c83 = Column(Float, comment='')
    float_c84 = Column(Float, comment='')
    float_c85 = Column(Float, comment='')
    float_c86 = Column(Float, comment='')
    float_c87 = Column(Float, comment='')
    float_c88 = Column(Float, comment='')
    float_c89 = Column(Float, comment='')


cashflow_column = [f"float_c{i+1}" for i in range(89)]


"""

class formCashFlow(formFinanceTemplate):
    __tablename__ = 'cashflow'
    report_period = Column(Date, primary_key=True)
    stock_code = Column(String(10), primary_key=True)
    r1_net_profit = Column(Float, comment='')
    r2_minority_interest = Column(Float, comment='')
    r3_unaffirmed_investment_loss = Column(Float, comment='')
    r4_impairment_of_fixed_asset = Column(Float, comment='')
    r5_depreciation_of_fixed_asset = Column(Float, comment='')
    r6_amortization_of_intangible_asset = Column(Float, comment='')
    r7_deferred_asset = Column(Float, comment='')
    r8_ = Column(Float, comment='')
    r9_ = Column(Float, comment='')
    r10_loss_on_disposal_asset = Column(Float, comment='')
    r11_loss_on_scrapping_of_fixed_asset = Column(Float, comment='')
    r12_ = Column(Float, comment='')
    r13_ = Column(Float, comment='')
    r14_accrued_liabilities = Column(Float, comment='')
    r15_finance_expense = Column(Float, comment='')
    r16_invesetment_loss = Column(Float, comment='')
    r17_ = Column(Float, comment='')
    r18_ = Column(Float, comment='')
    r19_decrease_in_inventory = Column(Float, comment='')
    r20_decrease_in_operating_receivables = Column(Float, comment='')
    r21_increase_in_operating_payables = Column(Float, comment='')
    r22_ = Column(Float, comment='')
    r23_ = Column(Float, comment='')
    r24_other = Column(Float, comment='')
    r25_net_cashflow_from_operating_activities = Column(Float, comment='')
    r26_ = Column(Float, comment='')
    r27_ = Column(Float, comment='')
    r28_ = Column(Float, comment='')
    r29_cash_at_the_end_of_period = Column(Float, comment='')
    r30_cash_at_the_beginning_of_period = Column(Float, comment='')
    r31_cash_equivalent_at_the_end_of_period = Column(Float, comment='')
    r32_cash_equivalent_at_the_beginning_of_period = Column(Float, comment='')
    r33_net_increase_in_cash_and_cash_equivalent = Column(Float, comment='')


"""


class formCapitalRelativeMatrix(Base):
    __tablename__ = 'capital_relative_matrix'
    stock_1 = Column(String(10), primary_key=True)
    stock_2 = Column(String(10), primary_key=True)
    relative = Column(Float, comment='')
    update_date = Column(Date, comment='')

class formInvestValueTemplate(Base):
    __tablename__ = 'invest_value_template'
    trade_date = Column(Date, comment='')

if __name__ == "__main__":
    x = [f"c{i+1}" for i in range(90)]
    print(x[-1])
