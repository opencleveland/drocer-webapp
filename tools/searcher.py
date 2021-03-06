#
# tools/searcher.py
#
# Try out queries on the Whoosh index.
#

TOOL_NAME = 'Drocer Searcher'
INDEX_PATH = '../data/index/city-record'

import jsonpickle
import os
import timeit

import whoosh.fields
import whoosh.index
import whoosh.qparser
from whoosh.query import *

from modules.document_structure import DrocerSerializable
from modules.document_structure import DrocerDocument
from modules.document_structure import DrocerPage
from modules.document_structure import DrocerBox

if __name__ == '__main__':

    # Setup logging.
    import logging
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)s: %(module)s.%(funcName)s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger.info('Starting %s.' % TOOL_NAME)
    logger.info('Reading Whoosh index from %s.' % INDEX_PATH)

    # Setup timer.
    start_time = timeit.default_timer()

    # Create searcher.
    whoosh_index = whoosh.index.open_dir(INDEX_PATH)
    whoosh_searcher = whoosh_index.searcher()

    # Create parser.
    whoosh_parser = whoosh.qparser.MultifieldParser(
        ["title", "content", "ordres_numbers", "parcel_numbers"],
        schema = whoosh_index.schema
    )

    # Define a query.
    default_queries = [
        'bids',
        'contracts',
        'taxi',
        '106-08-083'
    ]
    query_strings = default_queries
    waiting_time_start = timeit.default_timer()
    query_input = raw_input('Enter a query or leave blank for default queries: ')
    waiting_time_stop = timeit.default_timer()
    if query_input:
        query_strings = [query_input]

    # Get search results.
    for query_string in query_strings:
        whoosh_query = whoosh_parser.parse(query_string)
        whoosh_results = whoosh_searcher.search(whoosh_query, terms=True)
        whoosh_results.fragmenter.charlimit = None # turn off length limit for highlights
        print('Search: %s' % query_string)
        for hit in whoosh_results:
            #logger.debug('Loading JSON document: %s' % hit.fields()['structured_document_path'])#debug
            document = DrocerDocument.load(hit.fields()['structured_document_path'])
            print('Search hit:\n    document title: %s\n    highlight: %s\n    terms: %s' % (
                    hit['title'],
                    hit.highlights('content').replace('\n', ' ')[:64],
                    repr(hit.matched_terms())
            ))
            for term in hit.matched_terms():
                boxes = document.get_boxes_for_term(term)
                for box in boxes:
                    if len(term[1]) > len(query_string) / 2: # ignore short matches
                        print('        field %s term "%s" page %s box: %s: %s' % (
                            term[0],
                            term[1],
                            box.page_number,
                            box.number,
                            box.text.replace('\n', ' ')[:64]
                        ))

    # Close searcher.
    whoosh_searcher.close()

    elapsed = timeit.default_timer() - start_time - (waiting_time_stop - waiting_time_start)
    logger.info('%s complete.  Run time %ss' % (TOOL_NAME, elapsed))

