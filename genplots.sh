#!/bin/bash
TOPIC=athome1
RESULTS=./results.$TOPIC
PLOTS=./plots.$TOPIC
QRELS=~/CAL-P/data/$TOPIC.qrels
mkdir -p $PLOTS
cd $RESULTS

python ../rPlot.py $QRELS exponential static/k=1 static/k=100
mv a.pdf ../$PLOTS/bmi_static.pdf

python ../rPlot.py $QRELS static/k=1 partial/k=100,s=1000 partial/k=500,s=1000
mv a.pdf ../$PLOTS/static_partial.pdf

python ../rPlot.py $QRELS partial/k=100,s=1000 partial/k=100,s=5000 partial/k=100,s=100
mv a.pdf ../$PLOTS/partial2.pdf

python ../rPlot.py $QRELS precision/p=1.0,m=25 precision/p=0.8,m=25 precision/p=0.4,m=25
mv a.pdf ../$PLOTS/precision.pdf

python ../rPlot.py $QRELS static/k=1,it=100000 static/k=1,it=10000 static/k=1,it=1000 static/k=1,it=100 
mv a.pdf ../$PLOTS/training.pdf

python ../rPlot.py $QRELS recency/w=10,it=1000 static/k=1,it=100000 static/k=1,it=1000
mv a.pdf ../$PLOTS/recency.pdf

# cd ../results.bak
# python ../x.py ~/CAL/judgement/qrels.athome1.list ../results.100000/static/k=1 precision/p=0.6,k=25 precision/p=0.8,k=25 precision/p=1.0,k=25 
# # ../results.100000/precision/p=0.4,k=25
# mv a.pdf ../plots/prec2.pdf
