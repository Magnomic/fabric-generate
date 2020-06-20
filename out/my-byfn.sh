#!/bin/bash

CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org1.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA1_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org2.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA2_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org3.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA3_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org4.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA4_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org5.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA5_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
CURRENT_DIR=$PWD
cd   crypto-config/peerOrganizations/org6.example.com/ca/
PRIV_KEY=$(ls *_sk)
cd "$CURRENT_DIR"
sed -i "s/CA6_PRIVATE_KEY/${PRIV_KEY}/g" docker-compose-e2e.yaml
