#! /bin/sh

# Adds the newly created Proposer asset and adds it to Respondent elements.conf
# Adds the newly created Respondent asset and adds it to Proposer elements.conf

echo "Added $ASSET2:new-respondent-tkn to $C1 file"
echo "Added ac5ced10d3aa2a0a3d06835b8f0febc28eaf7b5383baf802bcf135266e6b08ad:dummy-nobalance-onlyrecv to $C1 file"
echo "assetdir=$ASSET2:new-respondent-tkn" >> $C1
echo "assetdir=ac5ced10d3aa2a0a3d06835b8f0febc28eaf7b5383baf802bcf135266e6b08ad:dummy-nobalance-onlyrecv" >> $C1

echo "Added $ASSET1:new-proposer-tkn to $C2 file"
echo "assetdir=$ASSET1:new-proposer-tkn" >> $C2
