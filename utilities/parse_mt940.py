#!/usr/bin/env python
# -*- encoding: utf-8 -*-
fname = '/home/robert/Documents/redo2oo/finanzen/bank/MT940_220418.sta'
# import mt940                                                           
# import pprint                    
# transactions = mt940.parse(fname) 
# for t in transactions:                                                 
#     if 'energie' in t.data['transaction_details'].lower():                
#         print t.data['date']
#         print t.data['transaction_details']
    


# -*- coding: utf-8 -*-
# © 2015-2016 Akretion
# © 2016 AbAKUS it-solutions
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# @author Valentin Thirion <valentin.thirion@abakusitsolutions.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from lxml import etree
import xlwt
import os

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(object):
    data_file = None
    
    def __init__(self, file_name):
        try:
            self.file_name = file_name
            self.data_file = open(file_name).read()
        except:
            raise

    def _check_camt(self, data_file):
        try:
            root = etree.fromstring(
                data_file, parser=etree.XMLParser(recover=True))
            ns = root.tag
            if not ns.startswith('{urn:iso:std:iso:20022:tech:xsd:camt.'):
                return False
        except:
            return False
        return root

    def _parse_file(self):
        """
        Parse the CAMT XML file
        """
        camt = self._check_camt(self.data_file)
        if not camt:
            _logger.debug("Statement file was not a camt file.")
            return 
        ns = camt.tag[1:camt.tag.index("}")]
        camt_type = ns[36:39]
        assert camt_type in ('052', '053'), 'wrong camt type'
        if camt_type == '052':
            body_tag = 'Rpt'
        else:
            body_tag = 'Stmt'

        # Account number
        iban_xpath = camt.xpath(
            '//ns:%s/ns:Acct/ns:Id/ns:IBAN' % body_tag, namespaces={'ns': ns})
        account_number = iban_xpath[0].text
        # Statement name
        statement_name_xpath = camt.xpath(
            '//ns:GrpHdr/ns:MsgId', namespaces={'ns': ns})
        statement_name = statement_name_xpath[0].text
        # Statement date
        statement_date_xpath = camt.xpath(
            '//ns:GrpHdr/ns:CreDtTm', namespaces={'ns': ns})
        statement_date = statement_date_xpath[0].text

        # Starting balance
        start_balance = 0
        camt_balances = camt.xpath(
            '//ns:%s/ns:Bal' % body_tag, namespaces={'ns': ns})
        for balance in camt_balances:
            balance_type = balance.xpath(
                'ns:Tp/ns:CdOrPrtry/ns:Cd', namespaces={'ns': ns})
            type_str = balance_type[0].text
            if type_str == 'OPBD':
                balance_amt = balance.xpath('ns:Amt', namespaces={'ns': ns})
                amount_str = balance_amt[0].text
                
                # Check if debit or credit
                balance_ind = balance.xpath('ns:CdtDbtInd', namespaces={'ns': ns})
                balance_ind_str = balance_ind[0].text
                if balance_ind[0].text == "CRDT":
                    start_balance = float(amount_str)
                if balance_ind[0].text == "DBIT":
                    start_balance = (float(amount_str)) * -1

        currency = False
        transactions = []
        camt_entries = camt.xpath(
            '//ns:%s/ns:Ntry' % body_tag, namespaces={'ns': ns})
        end_balance = start_balance
        for entry in camt_entries:
            entry_amt = entry.xpath('ns:Amt', namespaces={'ns': ns})
            amount_str = entry_amt[0].text
            amount = float(amount_str)
            entry_currency = entry.xpath('ns:Amt/@Ccy', namespaces={'ns': ns})
            line_currency = entry_currency[0].upper()
            if not currency:
                currency = line_currency
            elif currency != line_currency:
                raise UserError(_(
                    "The statement line with amount %s has a currency "
                    "%s which is different from the currency of the "
                    "other lines (%s).")
                    % (amount_str, line_currency, currency))
            entry_sign = entry.xpath('ns:CdtDbtInd', namespaces={'ns': ns})
            partner_tag = 'Dbtr'
            if entry_sign[0].text == 'DBIT':
                amount *= -1
                partner_tag = 'Cdtr'
            entry_date = entry.xpath('ns:BookgDt/ns:Dt', namespaces={'ns': ns})
            date = entry_date[0].text
            entry_partner_name = entry.xpath(
                'ns:NtryDtls//ns:RltdPties/ns:%s/ns:Nm' % partner_tag,
                namespaces={'ns': ns})
            partner_name = ""
            if len(entry_partner_name) > 0:
                partner_name = entry_partner_name[0].text
            entry_rmtinfo = entry.xpath(
                'ns:NtryDtls//ns:RmtInf/ns:Ustrd', namespaces={'ns': ns})
            label = ';'.join(line.text for line in entry_rmtinfo)
            entry_additional_info = entry.xpath(
                'ns:AddtlNtryInf', namespaces={'ns': ns})
            label += ':::'
            label += entry_additional_info[0].text
            
            transactions.append({
                'date': date,
                'ref': '',
                #'name': u'%s | %s' % (partner_name, label),
                'name': partner_name,
                'amount': amount,
                'unique_import_id': label
                #u'%s-%s-%s-%s' % (date, amount, partner_name, label),
                })
            end_balance += amount

        vals_bank_statement = {
            'name': statement_name,
            'transactions': transactions,
            'balance_start': start_balance,
            'balance_end_real': end_balance,
            'date': statement_date,
            # TODO : add real support for balances read from camt file
            }
        for transact in transactions:
            print(transact)
        return currency, account_number, [vals_bank_statement]
    
    def write_xls(self):
        currency, account_number, statements = self._parse_file()
        wb = xlwt.Workbook()
        sheet = wb.add_sheet(account_number)
        for statement in statements:
            balance_end = "{:10.2f}".format(statement['balance_end_real'])
            balance_start = "{:10.2f}".format(statement['balance_start'])
            transactions = statement['transactions']
            row = 0
            sheet.write(row, 0, balance_start)
            sheet.write(row, 1, balance_end)
            cols = [(0, 'amount'), (2, 'date'), (3, 'name'), (4, 'ref'), (5, 'unique_import_id')]
            for transaction in transactions:
                row += 1
                for col, n in cols[:-1]:
                    v = transaction[n]
                    if n == 'amount':
                        if v < 0:
                            col += 1
                    sheet.write(row, col, v)
                sub_t, sub_a = transaction[cols[4][1]].split(':::')
                sub_a = sub_a.split(',')
                col += 1
                for v in sub_t.split(';'):
                    sheet.write(row, col, v)
                    if sub_a:
                        sheet.write(row, col+1, sub_a.pop(0))
                    row += 1
                    
        o_name = '%s.xls' % os.path.splitext(self.file_name)[0]
        wb.save(o_name)
        
    def p940(self):
        import mt940                                                          
        import pprint 
                 
        transactions = mt940.parse(self.file_name) 
        for t in transactions:                                                 
            if 1: #'energie' in t.data['transaction_details'].lower():                
                print(t.data['date'])
                print(t.data['transaction_details'])
        
    

#camt_file = '/home/robert/Documents/redo2oo/finanzen/bank/CAMT053_220318.xml'
camt_file = '/home/robert/Documents/redo2oo/finanzen/bank/MT940_220418.sta'
handler = AccountBankStatementImport(camt_file)
handler.p940()

#for f in ['CAMT053_220418.xml', 'camt.053_P_CH2609000000616109340_313577883_0_2018050103531617.xml']:
    #handler = AccountBankStatementImport('/home/robert/Documents/redo2oo/finanzen/post/%s' % f)
    ##handler.p940()
    #handler.write_xls()