# NewEggPriceChecker

This script was updated in 2023 for python 3.7+, from python 2 in 2010. 

Please edit the URLs of the items you'd like the script to keep tabs on, and when the price changes, 
the script will call `espeak-ng` to announce verbally that the price has changed. 

This keeps track of multiple items concurrently by implementing multithreading for the price
checking, and a single "speech" thread that uses a queue so the speech is not garbled. 

If the price changes, the URL and prices are written both to the console and a newegg.txt file. 
Edit `time_between` to adjust the number of seconds between checks. 

Lucas
