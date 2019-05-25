#!/usr/bin/python
from dbConnect import *
import pandas as pd

def getEstFirstPosBid(cursor, keyword):
    '''
        returns est first pos bid for the keyword
    '''
    query = "select sum(est_first_pos_bid) from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    return cursor.fetchone()[0]

def get_makemodelyear(cursor, keyword):
    '''
       returns make, model, year for the keyword 
    '''
    query = "select distinct substring(ad_group from \'%-MK_#\"%#\"-MO_%\' for \'#\') as make, substring(ad_group from \'%-MO_#\"%#\"-YR_%\' for \'#\') as model,2000 + Cast( RIGHT(ad_group, 2)AS INT) as year \
                from kw_attributes \
                where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    ans = cursor.fetchone()
    return ans[0], ans[1], ans[2]


def get_mkmo_ARS(cursor, mkmo):
    '''
        returns make_model_ars value for the specified make and model
    '''
    query = "Select asr from make_model_asr where LOWER(makemodel) = LOWER(\'"+ mkmo+"\');"
    cursor.execute(query)
    return cursor.fetchone()[0]

def getConversionandRate(cursor, attribute, value):
    '''
        returns the no of conversions and conversion rate for the attribute
    '''
    if attribute == 'keyword':
        query = "select sum(perf.conversion) as conversion, sum(perf.conversion)/CAST(sum(perf.clicks) as double precision) as cvr \
                    from kw_performance perf \
                    join kw_attributes attr \
                    on attr.kw_id = perf.kw_id \
                    where LOWER(attr.keyword) = LOWER(\'"+value[0]+"\');"

    elif attribute == 'ad_group':
        query = "select conversion, cvr \
                    from ad_group_data \
                    where LOWER(ad_group) = LOWER(\'"+value[0]+"\');"

    elif attribute == 'mk_mo':
        query = "select conversion, cvr \
                    from mk_mo_data \
                    where LOWER(make) = LOWER(\'"+value[0]+"\') and LOWER(model) = LOWER(\'"+value[1]+"\');"

    elif attribute == 'mk_mo_yr':
        query = "select conversion, cvr \
                    from mk_mo_yr_data \
                    where LOWER(make) = LOWER(\'"+value[0]+"\') \
                    and LOWER(model) = LOWER(\'"+value[1]+"\') and year = "+str(value[2])+";"

    elif attribute == 'mkt':
        query = "select conversion, cvr \
                    from mkt_data where LOWER(mkt) = LOWER(\'"+value[0]+"\');"

    cursor.execute(query)
    row = cursor.fetchone()
    return row [0], row[1]

def new_bid_calc(cursor, keyword):
    '''
        calculated the new bid price
    '''
    make, model, year = get_makemodelyear(cursor, keyword)
    mk_mo_ars = get_mkmo_ARS(cursor, make + " " + model)

    kw_conv, kw_cvr = getConversionandRate(cursor, 'keyword', [keyword])
    if kw_conv > 10:
        return [kw_cvr * mk_mo_ars, 0]

    query = "select distinct ad_group from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    rows = cursor.fetchall()
    ad_conv, ad_cvr = 0, 0
    for ad_group in rows:
        temp = getConversionandRate(cursor, 'ad_group', [ad_group[0]])
        ad_conv += temp[0]
        ad_cvr += temp[1]
    if kw_conv < 11 and ad_conv > 10:
        return [ad_cvr * mk_mo_ars, 0]
 
    mk_mo_yr_conv, mk_mo_yr_cvr = getConversionandRate(cursor, 'mk_mo_yr', [make, model, year])
    if ad_conv < 11 and mk_mo_yr_conv > 10:
        return [mk_mo_yr_cvr * mk_mo_ars, 1]

    mk_mo_conv, mk_mo_cvr = getConversionandRate(cursor, 'mk_mo', [make, model])
    if mk_mo_yr_conv < 11 and mk_mo_conv > 10:
        return [mk_mo_cvr * mk_mo_ars, 1]

    if mk_mo_conv < 11:
        return [getEstFirstPosBid(cursor, keyword), 1]

def revised_bid(cursor, keyword, bid):
    '''
        revises the calculated new bid price acc to Step 2 ( 1a, 1b, 1c)
    '''
    changed_bid = bid[0]
    make, model, year = get_makemodelyear(cursor, keyword)
    mk_mo_ars = get_mkmo_ARS(cursor, make + " " + model)

    query = "select sum(currentOnsiteInventory) from inventory_current_onsite where LOWER(make) = LOWER(\'" + make + "\') and LOWER(model) = LOWER(\'" + model + "\') and year = " + str(year) + ";"
    cursor.execute(query)
    cur_inv = cursor.fetchone()[0]

    query = "select sum(HistAvgInv) from inventory_historical where LOWER(make) = LOWER(\'" + make + "\') and LOWER(model) = LOWER(\'" + model + "\') and year = " + str(year) + ";"
    cursor.execute(query)
    hist_inv = cursor.fetchone()[0]

    if cur_inv < hist_inv:
        percentage_reduce = ((hist_inv - cur_inv)/float(hist_inv) ) * 50
        changed_bid = (percentage_reduce * bid[0]) / 100

    if bid[1] == 1:
        query = "select avg(md.cvr) \
                from mkt_data md \
                join (select distinct substring(ad_group from \'%-_-#\"%#\"-MK_%\' for \'#\') as mkt \
                        from kw_attributes \
                        where LOWER(keyword) = LOWER(\'" + keyword + "\')) mk \
                on md.mkt = mk.mkt;"
        cursor.execute(query)
        mkt_cvr = cursor.fetchone()[0]

        query = "select sum(conversion)/CAST(sum(clicks)as double precision) as cvr from kw_performance;"
        cursor.execute(query)
        overall_cvr = cursor.fetchone()[0]
        changed_bid = ((overall_cvr - mkt_cvr) / 2) * bid[0]

    query = "select avg(qs) from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    qs = cursor.fetchone()[0]
    query = "select sum(est_first_pos_bid) from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    est_first_pos = cursor.fetchone()[0]
    query = "select sum(est_top_page_bid) from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\');"
    cursor.execute(query)
    est_top_page = cursor.fetchone()[0]
    if qs > 7 and bid[0] > est_first_pos:
        changed_bid = est_first_pos

    elif qs < 8 and qs > 5:
        query = "select avg(est_top_page_bid) from kw_attributes;"
        cursor.execute(query)
        avg_top_page = cursor.fetchone()[0]
        if bid[0] > est_first_pos and bid[0] > avg_top_page:
            changed_bid = max( est_first_pos, avg_top_page)

    elif qs < 6:
        value = (est_top_page * 0.9) + (est_first_pos * 0.1)
        if bid[0] > value:
            changed_bid = value

    if changed_bid > 12 or bid[0] > 12:
        changed_bid = 12.0
    return changed_bid

def revise2_bid(cursor, bid, keyword, final_bid):
    '''
        revises the calculated bid price acc to STep 2 (1d)
    '''
    query = "select distinct keyword from kw_attributes \
                where ad_group in (select distinct ad_group from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\') )\
                and LOWER(match_type) = \'exact\';"
    cursor.execute(query)
    rows = cursor.fetchall()
    min_group_bid = 12.0
    for keyword in rows:
        min_group_bid = min(min_group_bid, final_bid[keyword[0]])
    for keyword in rows:
        if bid > final_bid[keyword[0]]:
            bid = min_group_bid
            break
    return bid

def main():
    if len(sys.argv) < 3:
        print "Specify postgres username and password as argument."
        sys.exit(1)

    dbname = 'carvana'
    host = 'localhost'
    user = sys.argv[1]
    pwd = sys.argv[2]
    conn = connect_to_db(dbname, host, user, pwd)
    cursor = conn.cursor()
    
    query = "select distinct keyword from kw_attributes;"
    cursor.execute(query)
    keywords = cursor.fetchall()
    final_bid = dict()
    for keyword in keywords:
        new_bid = new_bid_calc(cursor, keyword[0])
        final_bid[keyword[0]] = revised_bid(cursor, keyword[0], new_bid)

    for keyword in keywords:
        query = "select match_type from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword[0] + "\');"
        cursor.execute(query)
        match = cursor.fetchone()[0]
        if match.lower() == "broad":
            final_bid[keyword[0]] = revise2_bid(cursor, final_bid[keyword[0]], keyword[0], final_bid)

    file = open('bidupload.csv', 'w')
    file.write('{0},{1}\n'.format('keyword_id', 'bid'))
    for keyword in keywords:
        #print keyword[0]
        query = "select distinct kw_id from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword[0] + "\');"
        cursor.execute(query)
        rows = cursor.fetchall()
        for kw_id in rows:
            file.write('{0},{1}\n'.format(kw_id[0], final_bid[keyword[0]]))
    file.close()
    close_connection_db(conn)
    
if __name__ == '__main__':
    main()
 