import unittest
import metaquant
from src import go
from tests.testutils import testfile
import numpy as np


class TestFunction(unittest.TestCase):
    def testSingleInt(self):
        func=testfile('simple_func.tab')
        int=testfile('simple_int.tab')

        go_df = metaquant.metaquant('fn', pep_colname='peptide',
                                    func_file=func, int_file=int,
                                    ontology='go', sample_names={'s1': ['int']}, test=False)
        self.assertEqual(go_df.loc["GO:0022610"]['int'], np.log2(200))
        self.assertEqual(go_df.loc["GO:0008152"]['int'], np.log2(100))

    def testMultipleInt(self):
        func=testfile('multiple_func.tab')
        int=testfile('multiple_int.tab')

        go_df = metaquant.metaquant('fn', func_file=func,
                                    int_file=int,
                                    ontology='go',
                                    sample_names={'s1': ['int1', 'int2', 'int3']})
        self.assertEqual(go_df.loc['GO:0008152']['int1'], np.log2(10))
        self.assertEqual(go_df.loc['GO:0022610']['int2'], np.log2(30))
        # missing values (zeros, nans, NA's, etc) are turned into NaN's
        self.assertTrue(np.isnan(go_df.loc['GO:0000003']['int3']))

    def testDA(self):
        func=testfile('multiple_func.tab')
        int=testfile('int_ttest.tab')

        go_df = metaquant.metaquant('fn', func_file=func,
                                    int_file=int,
                                    ontology='go',
                                    sample_names={'s1': ['int1', 'int2', 'int3'],
                                                  's2': ['int4', 'int5', 'int6']},
                                    test=True)

        # make sure false is > 0.05 and trues are less than 0.05
        self.assertTrue(go_df['corrected_p']['GO:0008152'] > 0.05)
        self.assertTrue(go_df['corrected_p'][['GO:0022610','GO:0000003','GO:0032505']].le(0.05).all())

    def testSlimDown(self):
        func=testfile('func_eggnog.tab')
        int=testfile('int_eggnog.tab')
        go_df = metaquant.metaquant('fn', func_file=func,
                                    int_file=int,
                                    ontology='go',
                                    sample_names={'NS': ['int737NS', 'int852NS', 'int867NS'],
                                                  'WS': ['int737WS', 'int852WS', 'int867WS']},
                                    test=True, slim_down=True,
                                    paired=True)

        # test that all go terms are in slim
        # load slim
        go_dag, go_dag_slim = go.load_obos(slim_down=True)

        returned_gos = set(go_df['id'])

        self.assertTrue(returned_gos.issubset(go_dag_slim.keys()))

    def testCog(self):
        func=testfile('multiple_func.tab')
        int=testfile('multiple_int.tab')

        cog_df = metaquant.metaquant('fn', func_file=func,
                                    int_file=int,
                                    ontology='cog',
                                    sample_names={'s1': ['int1', 'int2', 'int3']})
        self.assertEqual(cog_df.loc["C"]['s1_mean'], np.log2((10+20+70)/3))
        self.assertEqual(cog_df.loc["N"]['int2'], np.log2(30))

    def testCogTTest(self):
        func=testfile('multiple_func.tab')
        int=testfile('int_ttest.tab')

        cog_df = metaquant.metaquant('fn', func_file=func,
                                    int_file=int,
                                    ontology='cog',
                                    sample_names={'s1': ['int1', 'int2', 'int3'],
                                                  's2': ['int4', 'int5', 'int6']},
                                    test=True)
        # make sure false is > 0.05 and trues are less than 0.05
        self.assertTrue(cog_df['corrected_p']['C'] > 0.05)
        self.assertTrue(cog_df['corrected_p'][['N','D']].le(0.05).all())


if __name__ == '__main__':
    unittest.main()