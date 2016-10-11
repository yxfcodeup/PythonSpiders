#!/bin/bash

source ~/.bashrc 
function getCurrentPath()
{
    local _tmp_=`echo $0|grep "^/"`
    if test "${_tmp_}"
    then
        dirname $0
    else
        dirname `pwd`/$0
    fi
}

workdir=$(getCurrentPath)
ttg="/."
ta=${workdir:${#workdir}-2:${#workdir}}
if [ "$ttg" = "$ta" ] 
then
    workdir=${workdir:0:-2}
fi
logfile="${workdir}/logs/run.log"


mysql -u userxdr -p << EOF
    use xdr ;
    show tables ;
    DROP table if exists tbl_url_unreviewed ;
    DROP table if exists tbl_url_feature ;
    DROP table if exists tbl_action ;
    DROP table if exists tbl_category ;
    DROP table if exists tbl_industry_ctg ;
    create table tbl_industry_ctg (
        id bigint not null auto_increment , 
        parentcategoryid bigint not null , 
        categoryid bigint not null , 
        primary key(id)
    ) default charset utf8 ;
    desc tbl_industry_ctg ;

    create table tbl_category (
        cid bigint not null , 
        categoryname varchar(255) not null , 
        isparent enum('0','1') not null , 
        primary key(cid)
    ) default charset utf8 ;
    desc tbl_category ;

    create table tbl_action (
        actionid bigint not null , 
        actionname varchar(255) not null , 
        primary key(actionid)
    ) default charset utf8 ;
    desc tbl_action ;

    create table tbl_url_feature (
        urlid bigint not null auto_increment , 
        url varchar(255) not null , 
        categoryid1 bigint not null , 
        categoryid2 bigint , 
        categoryid3 bigint , 
        actionid1 bigint not null , 
        actionid2 bigint , 
        actionid3 bigint , 
        origin enum('1','2','3') , 
        sync enum('0','1','2') , 
        primary key(urlid) , 
        foreign key(categoryid1) references tbl_category(cid) ,  
        foreign key(categoryid2) references tbl_category(cid) , 
        foreign key(categoryid3) references tbl_category(cid) , 
        foreign key(actionid1) references tbl_action(actionid) , 
        foreign key(actionid2) references tbl_action(actionid) ,
        foreign key(actionid3) references tbl_action(actionid)
    ) default charset utf8 ;
    desc tbl_url_feature ;

    create table tbl_url_unreviewed (
        urlid bigint not null auto_increment , 
        url varchar(255) not null , 
        categoryid1 bigint , 
        categoryid2 bigint , 
        categoryid3 bigint , 
        actionid1 bigint , 
        actionid2 bigint , 
        actionid3 bigint , 
        isreviewed enum('0','1') ,
        primary key(urlid) , 
        foreign key(categoryid1) references tbl_category(cid) ,  
        foreign key(categoryid2) references tbl_category(cid) , 
        foreign key(categoryid3) references tbl_category(cid) , 
        foreign key(actionid1) references tbl_action(actionid) , 
        foreign key(actionid2) references tbl_action(actionid) ,
        foreign key(actionid3) references tbl_action(actionid)
    ) default charset utf8 ;
    desc tbl_url_unreviewed ;

    show tables ;
EOF
