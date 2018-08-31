# -*- coding: utf-8 -*-
import os
import odoorpc
import xlrd
import xlwt
import argparse

HOST = 'localhost'
PORT = 8069
DB = 'afbschweiz'
USER = 'admin'
PW = 'admin'
HEADER_LINE = 'Membership, parent-id, parent-name, partner-id, found, url, name, zip, city, street, fehlt, start, end'
FILE_NAME = '/home/robert/members.xls'
class MemberLister(object):
    mtypes = {}
    bad_parent = {}
    
    def __init__(self, opts):
        self.opts = opts
        odoo = odoorpc.ODOO(HOST, port=PORT)
        odoo.login(DB, USER, PW)
        self.odoo = odoo
        
    def listMembershipTypes(self):
        products = self.odoo.env['product.product']
        plist = products.browse(products.search([]))
        for p in plist:
            self.mtypes[p.name] = p.product_tmpl_id
            
    def _getPartners(self):
        pdomains = self.odoo.env['product.domain.list']
        # make sure we have the membership types
        self.listMembershipTypes()
        mtypes = list(self.mtypes.keys())
        mtypes.sort()
        pps = []
        for mtype in mtypes:
            domains = pdomains.browse(pdomains.search([('partner_dom', '=', self.mtypes[mtype].id)]))
            for domain in domains:
                pps.append({'mtype' : mtype, 'data' : domain})
                #owner = partners.search([('id', '=', domain.partner_id)])
        return pps
            
    def writeListMembershipOwners(self):
        # membership is defined by an entry in the
        # domain list
        # the domainlist links membership products to 
        # members
        self.process_file(self._getPartners())
        
        
    def _search_is_member(self):
        """The purpose of this function is to allow usage of the compute field
            'is_member' in searchview filter. Returns domain, to filter contacts list."""
        partners = self.odoo.env['res.partner']
        pdomain = self.odoo.env['product.domain.list']
        rec = partners.browse(partners.search([]))
        rec_ids = []
        for i in rec:
            if i.assigned_membership_list:
                product_domain_list = pdomain.search(
                    [('partner_id', '=', i.id),
                     ('partner_dom', '=', i.assigned_membership_list[0].m_type.id)])
                if product_domain_list:
                    rec_ids.append(i.id)
                else:
                    pass
        return rec_ids
        
                
    def process_file(self, data):
        assigned_partners = self.odoo.env['afbs.assigned_partner']
        wb = xlwt.Workbook()
        new_sheet = wb.add_sheet('names')
        # add the header line
        c = 0
        for f in HEADER_LINE.split(','):
            new_sheet.write(0, c, f.strip())
            c += 1
        c = -1
        rowcounter = 0
        found = self._search_is_member()
        for elem in data:
            rowcounter += 1
            c = 0
            new_sheet.write(rowcounter, c, elem['mtype'])
            d = elem['data']
            fc = ['','']
            if d.partner_id.id in self.bad_parent:
                bp = self.bad_parent[d.partner_id.id ]
                fc=[bp.id, bp.name]
            missing_assigned_partner = 'X'
            start = ''
            end = ''
            assigned_partner = assigned_partners.browse(assigned_partners.search([('partner', '=', d.partner_id.id)]))
            if assigned_partner:
                missing_assigned_partner = ''
                try:
                    start = assigned_partner.membership_start.strftime('%d, %b %Y')
                except:
                    start = ''
                end = ''
                try:
                    end = assigned_partner.membership_stop.strftime('%d, %b %Y')
                except:
                    end = ''
            for v in (
                    fc[0],
                    fc[1],
                    d.partner_id.id, 
                    d.partner_id.id in found and 'X' or '', 
                    d.domain_data, 
                    d.partner_id.name, 
                    d.partner_id.zip, 
                    d.partner_id.city,
                    d.partner_id.street,
                    missing_assigned_partner,
                    start,
                    end):
                c+= 1
                new_sheet.write(rowcounter, c, v)
            print(rowcounter)
            
        wb.save(self.opts.output)
        
    def reasign_membership(self):
        # params = self.odoo.env.context.get('params', {})
        # partner = params.get('active_id')
        """
        -----------------------------------------------------------------------
        {u'membership_start': u'2018-02-28', u'm_type': 49}
        -----------------------------------------------------------------------
        -----------------------------------------------------------------------
        {'membership_stop': False, 'partner': 4133, 'associated_partner': 2474, 'membership_start': '2018-02-28', 'm_type': 49}
        -----------------------------------------------------------------------
        
        select ap.id, pt.name, rp.name, rp.id, rp.email, pdl.partner_dom  from afbs_assigned_partner ap
	inner join product_template pt on pt.id = ap.m_type
	left outer join res_partner rp on rp.id = ap.partner
	left outer join product_domain_list pdl on pdl.partner_id = ap.partner
        """
        assigned_partners = self.odoo.env['afbs.assigned_partner']
        pps = self._getPartners()
        for elem in pps:
            # 
            d = elem['data']
            start = ''
            end = ''
            assigned_partner = assigned_partners.browse(assigned_partners.search([('partner', '=', d.partner_id.name)]))
            if assigned_partner:
                params = {'active_id': d.partner_id.id}  
                try:
                    params['membership_start'] = assigned_partner.membership_start.strftime('%Y-%m-%d')
                except:
                    pass
                end = ''
                if assigned_partner.membership_stop:
                    try:
                        params['membership_stop'] = assigned_partner.membership_stop.strftime('%Y-%m-%d')
                    except:
                        pass
                if not d.partner_id.name:
                    print('no name:%s '% d.partner_dom.name, d.domain_data)
                else:
                    print(d.partner_id.name)
                    #assigned_partners.create(vals=params)
            else:
                print('>>(%s)'% d.partner_dom.name, d.partner_id.name, 'not found')
            
        
    def check_hierarchy(self):
        pdomain = self.odoo.env['product.domain.list']
        for pd in pdomain.browse(pdomain.search([])):
            p = pd[0].partner_id
            if p.parent_id:
                print('--------->', pd[0].id, p.id, p.name, pd[0].partner_dom.name, p.parent_id[0].name)
                self.bad_parent[p.id] = p.parent_id[0]
                
    def _get_connection(self):
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect("dbname='afbschweiz' user='robert' host='localhost' password='admin'")
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
                
    def query_membership(self):
        wb = xlwt.Workbook()
        new_sheet = wb.add_sheet('query')
        cur = self._get_connection()
        
        q = """
        select ap.id, pt.name, rp.name, rp.id, rp.email, pdl.partner_dom, pdl.domain_data, ap.membership_start, ap.membership_stop  from afbs_assigned_partner ap
	inner join product_template pt on pt.id = ap.m_type
	left outer join res_partner rp on rp.id = ap.partner
	left outer join product_domain_list pdl on pdl.partner_id = ap.partner
        order by pt.name
        """
        header = [
            'assigned_partner id', 'membership', 'partner name', 'partner id', 'partner email', 'id domain', 'domain', 'assigned_partner membership_start', 'assigned_partner membership_stop'        
        ]
        c = 0
        rowcounter = 0
        for f in header:
            new_sheet.write(rowcounter, c, f.strip())
            c += 1 
        
        result = cur.execute(q)
        rows = cur.fetchall()
        for row in rows:
            rowcounter += 1
            c = -1
            for _ in header:
                c+= 1
                v = row[c]
                if isinstance(v, str):
                    v = v.decode('utf8')
                else:
                    if c == 7 and v:
                        v = v.strftime('%Y-%m-%d')
                new_sheet.write(rowcounter, c, v)
                print(v, end=' ')
            print()
        print('------->', rowcounter)
            
        wb.save(self.opts.output or FILE_NAME)
        
    def who_is(self):
        # import pythonwhois
        import dns.resolver
        cur = self._get_connection()
        q = 'select  distinct domain_data from product_domain_list order by domain_data'
        q2 = "select * from product_domain_list where domain_data = '%s'"
        q3 = """
        select ap.id, pt.name, rp.name, rp.id, rp.email, pdl.partner_dom, pdl.domain_data, 
            ap.membership_start, ap.membership_stop  from afbs_assigned_partner ap
        inner join product_template pt on pt.id = ap.m_type
        left outer join res_partner rp on rp.id = ap.partner
        right outer join product_domain_list pdl on pdl.partner_id = ap.partner
        where pdl.domain_data = '%s' 
        order by pt.name
        """
        cur.execute(q)
        rows = cur.fetchall()
        # details = pythonwhois.get_whois('ZUR.INVESCO.COM')
        for row in rows:
            try:
                #print row[0]
                #details = pythonwhois.get_whois(row[0])
                answers = dns.resolver.query(row[0], 'MX')
            except Exception as e:
                print('ERROR:', row[0])
                print(str(e))
                cur.execute(q2 % row[0])
                r = cur.fetchone()
                print(list(r.keys()))
                print(r['partner_id'],row[0])
                #cur.execute(q3 % (row[0], r['partner_id']))
                cur.execute(q3 % (row[0]))
                print(cur.fetchall())

                continue
            if answers:
                continue
                print('.', end=' ') #row[0], 
                for rdata in answers:
                    print('Host', rdata.exchange, 'has preference', rdata.preference) 
                print('---------------------------------')
            else:
                print('not found', row[0])
            

def main(opts):
    handler = MemberLister(opts)
    if opts.check_hierarchy:
        handler.check_hierarchy()
        
    if opts.query:
        handler.query_membership()
        return
    
    if opts.output:
        handler.listMembershipTypes()
        handler.check_hierarchy()
        handler.writeListMembershipOwners()
        
    if opts.reasign:
        handler.reasign_membership()
        
    if opts.who_is:
        handler.who_is()
            
        
        

if __name__ == '__main__':
    usage = "manage membership types" 
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument(
        "-cth", "--check-hierarchy",
        action="store_true", dest="check_hierarchy", default=False,
        help = 'name of the db to handle partners for'
    )
    parser.add_argument(
        "-o", "--ouput",
        action="store", dest="output",
        help = 'path to the excel sheet to output'
    )
    parser.add_argument(
        "-r", "--reasign",
        action="store_true", dest="reasign", default=False,
        help = 'reasign membersips'
    )
    parser.add_argument(
        "-q", "--query",
        action="store_true", dest="query", default=False,
        help = 'query membersips'
    )

    parser.add_argument(
        "-w", "--who-is",
        action="store_true", dest="who_is", default=False,
        help = 'who_is membersips'
    )
    args, unknownargs = parser.parse_known_args()
    main(args) #opts.noinit, opts.initonly)
        
