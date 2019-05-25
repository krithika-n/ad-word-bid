create table ad_group_data as select attr.ad_group as ad_group, sum(perf.conversion) as conversion, sum(perf.conversion)/CAST(sum(perf.clicks) AS Double precision) as cvr
from kw_performance perf
join (select kw_id, ad_group from kw_attributes) attr
on perf.kw_id = attr.kw_id
group by attr.ad_group;

create table mk_mo_yr_data as select attr.make as make, attr.model as model, attr.year as year, sum(perf.conversion) as conversion, sum(perf.conversion)/CAST(sum(perf.clicks) AS Double precision) as cvr
from kw_performance perf
join ( 
    select kw_id, substring(ad_group from '%-MK_#"%#"-MO_%' for '#') as make, substring(ad_group from '%-MO_#"%#"-YR_%' for '#') as model,2000 + Cast( RIGHT(ad_group, 2)AS INT) as year
    from kw_attributes ) attr
on perf.kw_id = attr.kw_id
group by attr.make, attr.model, attr.year;

create table mk_mo_data as select attr.make as make, attr.model as model, sum(perf.conversion) as conversion, sum(perf.conversion)/CAST(sum(perf.clicks) AS Double precision) as cvr
from kw_performance perf
join ( 
    select kw_id, substring(ad_group from '%-MK_#"%#"-MO_%' for '#') as make, substring(ad_group from '%-MO_#"%#"-YR_%' for '#') as model
    from kw_attributes ) attr
on perf.kw_id = attr.kw_id
group by attr.make, attr.model;

create table mkt_data as select attr.mkt as mkt, sum(perf.conversion) as conversion, sum(perf.conversion)/CAST(sum(perf.clicks) AS Double precision) as cvr
from kw_performance perf
join ( select kw_id, substring(ad_group from '%-_-#"%#"-MK_%' for '#') as mkt from kw_attributes ) attr
on perf.kw_id = attr.kw_id
group by attr.mkt;