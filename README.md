The purpose of the project is to do query expansion using Bing API.
The system gets query result from Bing API and process the Title and Description received to produce a set of relevant terms using tf-idf scoring.
The top scoring relevant terms are then added to the query to create the expanded query.
There are various features supported by the system using the parameters below in the Run Command section.
The system provides facility to provide user relevance feedback as well.

Run Command -  
Running command is
python main.py --key <bing account key>
--userFB <user feedback (Y or N), If Y then query expansion runs till target precision is reached If N then its auto mode>
--targetPrec <Precision to target, used when user feedback is on>
--f <file containing queries in format "MB051<newline>35124912364457984<newline>Feb 2011 British Government cuts<endOfFile>">
--Ngram <1|2 for Unigram or Bigram terms processing>
--ordering <Y or N for ordering or non-ordering the expanded query terms>
--posTagging <Y or N, Y means part of speech tagging is used. In this case, proper noun and verbs will be ignored for query expansion>
--maxWords <number of words to expand in one iteration>
--iter <no of iterations to run when run in auto mode, Default 1>
--iterResults <no of results to fetch from API for a query, Default is 10>

For example,  
python main.py --key JsV9AIVwzY0l654YiaIXAppMcpvpm7lvkcYdmzJrNcs --userFB N --f "queriesForBing.txt" --Ngram 2 --ordering N --posTagging N --maxWords 2 --iter 1 --iterResults 10
