#!/bin/sh

function create_account(){
  a=0

  while [ $a -lt 5000 ]
  do
       echo $a
       a=`expr $a + 1`
       python3 tx_sender.py local create samuel@nebulas
  done
}

function transfer(){
  filename="$1"
  from="n1aD4A2JKYboUAmWnKQv3LAmRmtiDPpSLPm"

  while read -r line; do
    addr="$line"
    python3 tx_sender.py local tx $from $addr 1.0 samuel@nebulas
  done < "$filename"
}

function testing(){
  filename="$1"

  to="n1aD4A2JKYboUAmWnKQv3LAmRmtiDPpSLPm"

  while read -r line; do
    addr="$line"
    echo "transfer from " $line
    python3 tx_sender.py local tx $addr $to 0.00001 samuel@nebulas &
  done < "$filename"
}

create_account
#testing $1
