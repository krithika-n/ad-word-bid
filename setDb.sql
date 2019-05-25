create database carvana;
\c carvana;

create table inventory_current_onsite(
    make text,
    model text,
    year integer,
    currentOnsiteInventory integer
    );

create table inventory_historical(
    make text,
    model text,
    year integer,
    HistAvgInv integer
    );

create table kw_attributes(
    campaign text,
    ad_group text,
    keyword text,
    kw_id integer,
    match_type text,
    qs integer,
    est_first_pos_bid double precision,
    est_top_page_bid double precision
    );

create table kw_performance(
    kw_id integer,
    impression text,
    clicks integer,
    cost double precision,
    conversion integer
    );

create table make_model_asr(
    makemodel text,
    make text,
    model text,
    asr double precision
    );
