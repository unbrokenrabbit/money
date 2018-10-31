#import sys
#sys.path.append('..')
#from .. import transactions
import transactions.translation.mint.csv as mint_csv
import test.test_mint_csv

test.test_mint_csv.run_all_tests()
