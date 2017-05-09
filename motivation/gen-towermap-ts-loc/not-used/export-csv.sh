#!/bin/bash

SRC_DIR=`cd "$( dirname "$0" )"; pwd`

schema() {
	dn=$SRC_DIR/.result/schema
	mkdir -p $dn
	mdb-schema ~/work/castnet-data/towermap-dec-2016/pgdb_FCC_ASR_December_2016.mdb > $dn/pgdb_FCC_ASR_December_2016.schema
	mdb-schema ~/work/castnet-data/towermap-dec-2016/TowerMaps_Dec_2016_COPYRIGHTEDuncompressed.mdb > $dn/TowerMaps_Dec_2016_COPYRIGHTEDuncompressed.schema
	mdb-schema ~/work/castnet-data/towermap-dec-2016/TowerMaps_Dec_2016.mdb > $dn/TowerMaps_Dec_2016.schema
}

select_() {
	dn=$SRC_DIR/.result
	mkdir -p $dn
	mdb-export ~/work/castnet-data/towermap-dec-2016/pgdb_FCC_ASR_December_2016.mdb CO_EB_latlong_Height > $dn/pgdb_FCC_ASR_December_2016.CO_EB_latlong_Height.csv
}

select_
