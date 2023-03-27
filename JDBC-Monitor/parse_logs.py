import glob
import os
import math
import argparse
import pathlib
import os.path
import sys
import csv
from io import StringIO

# ----------------------------------------------------------------------------------------------------------------------
def print_help_and_exit( message, parser ):
    if len( message ) > 0:
        print( message )
    
    s = '''
  
  This parser reads trace files and for each, it generates 2 output files. The 1st one contains the queries with their response time, 
  parameter values, and stack and the 2nd file is a grouping of the same queries with number of calls, percentiles and sum of resp. time.
  
  Usage
  -----
    python ''' + parser.prog + ''' 
        -p <path_to_trace_files>    Path where to look for trace files. If not provided, it defaults to current folder.
        
        -f <trace_file(s)>          Trace file(s) to parse. One trace file or more separated by commas. Wildcards can also be used.
        
        -c                          Concatenate the queries with their parameter values. The default is not to concatenate
                                    
        -g                          Grouping the trace files. The default is to not group and generate 2 query files for each trace file.
        
        -k <keyword>                This keyword parameter is used to filter the queries. Only the ones that have this keyword(s)
                                    in their stack will be added to the csv/XL files. Can use multiple keywords separated by comma.
                                    
        -u < all | any >            Usage of the keyword. This parameter is used when multiple keywords are used.
                                    If all is used. A query is picked if all keywords are found in the stack.
                                    If any is used. A query is picked if any keyword is found in the stack.
                                    This parameter is considered only if -k and multiple keywords are used.
                                    
        -o <output_folder>          Output folder where to save the output files. If not provided, it defaults to current folder.
        
        -h                          Print this help.

'''
    print( s )
    sys.exit( 1 )
# ----------------------------------------------------------------------------------------------------------------------
def calculate_percentile( arry, percentile ):
    size = len( arry )
    return sorted( arry )[ int( math.ceil( ( size * percentile ) / 100 ) ) - 1 ]
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------- MAIN -----------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser( description = 'Read trace logs and extract and sort queries and save all in a csv file', add_help = False )
parser.add_argument( '-p', type = pathlib.Path, help = 'Path where to look for trace files. Defaults to current folder' )
parser.add_argument( '-f', type = str, help = 'Trace file(s) to parse. One or multiple files separated by comma or wildcard' )
parser.add_argument( '-c', action = 'store_true', help = 'Concatenate the query with its parameter values' )
parser.add_argument( '-g', action='store_true', help = 'Group the queries from multiple trace files or treat each trace file appart. Default is not grouping the trace files' )
parser.add_argument( '-k', type = str, help = 'Considering only the queries that have keyword(s) in their stacks' )
parser.add_argument( '-u', type = str, help = 'Usage of the keywords. all => A query is added to the csv file if all keywords are found in the stack. any => it\'s added for any keyword' )
parser.add_argument( '-o', type = pathlib.Path, help = 'Output folder where to save the output files. Defaults to current folder' )
parser.add_argument( '-h', action='store_true', help = 'Print help' )

try:
    args = parser.parse_args()
except:
    print_help_and_exit( '', parser )

# ============================================
# Check the script's parameters
# ============================================
filenames = []
output_file_prefix = ''
output_folder = ''
path_to_trace_files = ''
keywords = []
filter_by_keywords = False
keyword_usage = 'none'
concat_query_with_params = False
group_files = False

# print( 'args = ', args )

# ============================================
# Argument -p
# ============================================
if args.p == None:
    path_to_trace_files = os.getcwd()
else:
    if os.name == 'nt':
        path_to_trace_files = pathlib.PureWindowsPath( args.p )
    elif os.name == 'posix':
        path_to_trace_files = pathlib.Path( args.p )
    else:
        print( '\n\nOperating system not recognizable. Exiting ... \n\n' )
        sys.exit( 1 )

# ============================================
# Argument -f 
# ============================================
if args.f != None:
    # Check if multiple files are provided
    if ',' in args.f:
        filenames = args.f.split( ',' )
        
        print( 'filenames = ', filenames )
        
        for i in range( len( filenames ) ):
            if args.p != None:
                filenames[ i ] = os.path.join( path_to_trace_files, filenames[ i ] )
            if '*' not in filenames[ i ]:
                if not os.path.isfile( filenames[ i ] ):
                    print_help_and_exit( 'Error: File {} specified by -f parameter does not exist'.format( filenames[ i ] ), parser )
            

        print( 'filenames = ', filenames )
        
    elif '*' not in args.f:
        if not os.path.isfile( os.path.join( path_to_trace_files, args.f ) ):
            print_help_and_exit( 'Error: File {} specified by -f parameter does not exist'.format( args.f ), parser )
        filenames.append( os.path.join( path_to_trace_files, args.f ) )
    else:
        if args.p != None:
            filenames.append( os.path.join( path_to_trace_files, 'trace*.log' ) )
        else:
            filenames.append( 'trace*.log' )
else:
    if args.p != None:
        filenames.append( os.path.join( path_to_trace_files, '*.log' ) )
    else:
        filenames.append( '*.log' )

# ============================================
# Argument -c
# ============================================
if args.c == True:
    concat_query_with_params = True

# ============================================
# Argument -g
# ============================================
if args.g == True:
    group_files = True

# ============================================
# Argument -k
# ============================================
if args.k != None:
    filter_by_keywords = True
    keywords = args.k.replace( ' ', '' ).split( ',' )

    # ============================================
    # Argument -u
    # ============================================
    if args.u != None:
        if len( keywords ) > 1:
            keyword_usage = args.u
            if keyword_usage not in [ 'any', 'all' ]:
                print_help_and_exit( 'Error: wrong value for keyword usage parameter (-u)', parser )
            keyword_usage = args.u
        elif len( keywords ) == 1:
            keyword_usage = 'any'
    else:
        keyword_usage = 'any'

# ============================================
# Argument -o
# ============================================
if args.o == None:
    output_folder = os.getcwd()
else:
    if os.name == 'nt':
        output_folder = pathlib.PureWindowsPath( args.o )
    elif os.name == 'posix':
        output_folder = pathlib.Path( args.o )
    else:
        print( '\n\nOperating system not recognizable. Exiting ... \n\n' )
        sys.exit(1)

# ============================================
# Argument -h
# ============================================
if args.h == True:
    print_help_and_exit( '', parser )

# ============================================
# Get all trace files
# ============================================
trace_files = []
for file in filenames:
    traces = glob.glob( file )
    trace_files.extend( traces )

# ============================================
# Display some info to the user
# ============================================
print( '\n\nTrace files folder               ', path_to_trace_files )
print( 'Output folder                    ', output_folder )

if len( trace_files ) == 1:
    print( 'Number of trace file found             1' )
elif len( trace_files ) > 1:
    print( 'Number of trace files found      ', len( trace_files ) )
else:
    print( 'There is no trace file found in the folder provided. Exiting ... ' )
    exit()

if len( keywords ) > 0:
    if len( keywords ) > 1:
        print( 'Keywords:                        ', ', '.join( keywords ) )
    else:
        print( 'Keyword:                         ', ', '.join( keywords ) )
    
    if len( keywords ) > 1:
        if keyword_usage == 'any':
            print( 'Usage of keywords                 ANY => Query is added to the csv file if any keyword is found in the stack' )
        else:
            print( 'Usage of keywords                 ALL => Query is added to the csv file if all keywords are found in the stack' )
else:
    print( 'Keyword:                         ', 'None' )
    print( 'Usage of keywords:               ', 'None' )
    
print( 'Grouping files?                  ', group_files )
print( 'Concat queries and parameters?   ', concat_query_with_params )

print()

# ============================================
# Init the main list for grouped queries
# ============================================
grouped_queries = []
sum_resp_time = []
nbr_calls = []
# Init the main list for individual queries
queries = []
response_times = []

# ============================================
# Prepare the non-sorted csv file
# ============================================
# Check if we need to create 2 files for each trace file or 2 files for all
if group_files == True:
    # Create queries file
    try:
        csvfile = open( os.path.join( str( output_folder ), 'allqueries.csv' ), 'w' )
    except:
        print( 'Error. Could not open ' + os.path.join( str( output_folder ), 'allqueries.csv' ) )
        exit()
    
    csvfile.write( 'Resp. time,Query,Parameters,Stack\n' )
    
    # Create grouped queries file
    try:
        csvfile_grouped = open( os.path.join( str( output_folder ), 'allqueries_grouped.csv' ), 'w' )
    except:
        print( 'Error. Could not open ' + os.path.join( str( output_folder ), 'allqueries_grouped.csv' ) )
        exit()
    csvfile_grouped.write( 'Nbr of Calls,Average resp. time,95-percentile,99-percentile,Sum of resp. time,Query\n' )
    
# ============================================
# Reading the trace files one by one
# ============================================
print( 'Reading the trace files' )
for file in trace_files:
    print( '   Reading from file', file )
    tracefile = open( file, 'r' )
    
    # Check if we're grouping the queries from multiple trace files in one file or not
    if group_files == False:
        file2open = os.path.join( str( output_folder ), 'allqueries_' + os.path.splitext( os.path.split( file )[ 1 ] )[ 0 ] + '.csv' )
        try:
            csvfile = open( file2open, 'w' )
        except:
            print( 'Error. Could not open file: ' + file2open )
            exit()
        csvfile.write( 'Resp. time,Query,Parameters,Stack\n' )
    nbr_queries = 0
    for line in tracefile:
        if ' JDBCMonitor ' in line and '"WSJdbcPreparedStatement' in line and '"durationMs"' in line and '"query"' in line:
            i = line.find( '"durationMs":' )
            if i > 0:
                line = line[ i + len( '"durationMs":' ) : ]
                j = line.find( ',"query":"' )
                if j > 0:
                    # Get response time
                    rt = float( line[ : j ].replace( ',', '' ).replace( '"', '' ) )
                    response_time = '"' + str( rt ) + '"'
                    
                    # Get the rest: query text, parameters and stack
                    i = line.find( '"query":' )
                    line = line[ i + len( '"query":' ) : ]
                                        
                    f = StringIO( line )
                    i = 0
                    query = param = stack = ''
                    for row in csv.reader( f, delimiter = ',', dialect = csv.excel ):
                        for r in row:
                            if i == 0:
                                query = '"' + r + '"'
                            elif i == 1:
                                param = r.replace( 'parameters:', '' )
                                if '}' not in param:
                                    i = -1
                                    continue
                                else:
                                    param = param[ 1:-1 ]
                            elif i == -1:
                                param += '-' + r
                                if '}' not in param:
                                    continue
                                else:
                                    i = 1
                                    param = param[ 1:-1 ]
                            elif i == 2:
                                stack = r.replace( 'stack:"["', '' ).replace( '"', '' )
                            else:
                                stack += '\n\t' + r 
                            i += 1
                    param = '"' + param + '"'
                    stack = '"' + stack + '"'
                    
                    # Check for keyword
                    if keyword_usage == 'none':
                        found = True
                    else:
                        found = False
                        if keyword_usage == 'any':
                            for keyword in keywords:
                                if keyword in stack:
                                    found = True
                                    break
                        elif keyword_usage == 'all':
                            for keyword in keywords:
                                if keyword not in stack:
                                    found = False
                                    break
                                else:
                                    found = True
                        if not found:
                            continue
                    
                    # Check if we should concatenate the query with its parameter values
                    if concat_query_with_params:
                        query += '  ' + param
                    
                    # Write to non-sorted csvfile (all queries file) 
                    csvfile.write( response_time + ',' + query + ',' + param + ',' + stack + '\n' )
                
                    # Save the current individual query and its respose time
                    queries.append( query )
                    response_times.append( rt )
                                        
                    if query in grouped_queries:
                        k = grouped_queries.index( query )
                        sum_resp_time[ k ] = sum_resp_time[ k ] + rt
                        nbr_calls[ k ] = nbr_calls[ k ] + 1
                    else:
                        grouped_queries.append( query )
                        sum_resp_time.append( rt )
                        nbr_calls.append( 1 )
                    
                    # Increment number of queries 
                    nbr_queries += 1
                else:
                    print( '     JDBCMonitor tag found but not query' )
            else:
                print( '     JDBCMonitor, WSJdbcPreparedStatement, durationMs or query not found in current line' )
    print( '      Read ' + str( nbr_queries ) + ' queries' )
    tracefile.close()
    
    print( '\nGrouping and sorting the queries' )

    # Prepare the sorted csv file
    if group_files == False:
        file2open = os.path.join( str( output_folder ), 'allqueries_grouped_' + os.path.splitext( os.path.split( file )[ 1 ] )[ 0 ] + '.csv' )
        try:
            csvfile_grouped = open( file2open, 'w' )
        except:
            print( 'Error. Could not open file: ' + file2open )
            exit()
        csvfile_grouped.write( 'Nbr of Calls,Average resp. time,95-percentile,99-percentile,Sum of resp. time,Query\n' )

    # Sort on resp. time
    while len( sum_resp_time ) > 0:
        # Get the index of the max response time
        i = sum_resp_time.index( max( sum_resp_time ) )
        
        # Get the average, 95-percentile and 99-percentile of the current query
        d = []
        for j in range( len( queries ) ):
            if queries[ j ] == grouped_queries[ i ]:
                d.append( response_times[ j ] )
        pct99 = calculate_percentile( d, 99 )
        pct95 = calculate_percentile( d, 95 )
        avg_rt = sum( d ) / len( d )
        
        # Format the floats 
        s_calls = '"' + '{:,}'.format( nbr_calls[ i ] ) + '"'
        s_avg = '"' + '{0:,.2f}'.format( avg_rt ) + '"'
        s_95 = '"' + '{0:,.2f}'.format( pct95 ) + '"'
        s_99 = '"' + '{0:,.2f}'.format( pct99 ) + '"'
        s_rt = '"' + '{0:,.2f}'.format( sum_resp_time[ i ] ) + '"'
        
        # Write to the grouped queries file
        csvfile_grouped.write( s_calls + ',' + s_avg + ',' + s_95 + ',' + s_99 + ',' + s_rt + ',' + grouped_queries[ i ] + '\n' )
        
        # Delete the max rows from the list
        grouped_queries.pop( i )
        sum_resp_time.pop( i )
        nbr_calls.pop( i )

    # Close the csv files
    if group_files == False:
        csvfile.close()
        csvfile_grouped.close()

print( '\nDone' )
