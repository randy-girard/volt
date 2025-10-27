#!/bin/bash

TEXT="[Sun Aug 11 10:51:53 2024] x05-something;"
DIR='/Users/rgirard/Desktop/EverQuest - P99.app/drive_c/Program Files/EverQuest/Logs'

echo "$TEXT" >> "$DIR/eqlog_Test_P1999Green.txt"
sleep .5
echo "$TEXT" >> "$DIR/eqlog_Test_P1999Green.txt"
sleep .5
echo "$TEXT" >> "$DIR/eqlog_Debits_P1999Green.txt"

sleep .5
echo "[Sun Aug 11 10:51:53 2024] **A Magic Die is rolled by Moonglade." >> "$DIR/eqlog_Debits_P1999Green.txt"
echo "[Sun Aug 11 10:51:53 2024] **It could have been any number from 0 to 1000, but this time it turned up a 40." >> "$DIR/eqlog_Debits_P1999Green.txt"
