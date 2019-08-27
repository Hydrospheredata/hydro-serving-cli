import os
import unittest

import numpy as np
import pandas as pd
from hydroserving.client import HSContract

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FILES_PATH = os.path.abspath('{}/../../examples/adult'.format(SCRIPT_DIR))


class TestApplicationFile(unittest.TestCase):

    def test_simple_model(self):
        with open(os.path.join(FILES_PATH, 'adult-scalar/serving.yaml')) as f:
            c = HSContract.load(f)

        with open(os.path.join(SCRIPT_DIR, 'test.yml'), "w+") as f:
            c.dump(f)

        self.assertIsNotNone(c)

        os.remove(os.path.join(SCRIPT_DIR, 'test.yml'))

    def test_input_dict_reconstruction(self):
        with open(os.path.join(FILES_PATH, 'adult-scalar/serving.yaml')) as f:
            c = HSContract.load(f)
            x_dict = dict(zip(c.input_names, np.ones(12, dtype="int")), )
            proto = c.make_proto(x_dict)
            x_dict_restored = HSContract.decode_list_of_tensors(proto)
            self.assertEqual(x_dict_restored, x_dict)

        with open(os.path.join(FILES_PATH, 'adult-tensor/serving.yaml')) as f:
            c = HSContract.load(f)
            x_dict = {c.input_names[0]: np.ones((1, 12), dtype="int")}
            proto = c.make_proto(x_dict)
            x_dict_restored = HSContract.decode_list_of_tensors(proto)
            self.assertEqual(x_dict_restored.keys(), x_dict.keys())
            np.testing.assert_array_equal(x_dict_restored['input'], x_dict['input'])

        with open(os.path.join(FILES_PATH, 'adult-columnar/serving.yaml')) as f:
            c = HSContract.load(f)
            x_dict = dict(zip(c.input_names, np.ones((12, 12, 1), dtype="int")))
            proto = c.make_proto(x_dict)
            x_dict_restored = HSContract.decode_list_of_tensors(proto)
            self.assertEqual(x_dict_restored.keys(), x_dict.keys())
            for tensor_name in c.input_names:
                np.testing.assert_array_equal(x_dict_restored[tensor_name], x_dict[tensor_name])

    def test_dataframe_to_input_dict(self):
        with self.subTest(msg="Adult Model, Scalar Contract"):
            with open(os.path.join(FILES_PATH, 'adult-scalar/serving.yaml')) as f:
                c = HSContract.load(f)
                df = pd.DataFrame(np.ones((1, 12), dtype="int"), columns=c.input_names)
                expected_dict = dict(zip(c.input_names, np.ones(12, dtype="int")), )
                constructed_dict = c.make_input_dict(df, {})
                self.assertTrue(c.verify_input_dict(expected_dict)[0])
                self.assertTrue(c.verify_input_dict(constructed_dict)[0])
                self.assertEqual(expected_dict, constructed_dict)

        with self.subTest(msg="Adult Model, Single Tensor Contract, Batch Included"):
            with open(os.path.join(FILES_PATH, 'adult-tensor/serving.yaml')) as f:
                c = HSContract.load(f)
                df = pd.DataFrame(np.ones((1, 12), dtype="int"))
                expected_dict = {c.input_names[0]: np.ones((1, 12), dtype="int")}
                constructed_dict = c.make_input_dict(df, {})
                self.assertTrue(c.verify_input_dict(expected_dict)[0])
                self.assertTrue(c.verify_input_dict(constructed_dict)[0])
                np.testing.assert_array_equal(expected_dict['input'], constructed_dict['input'])

        with self.subTest(msg="Adult Model, Columnar Contract, Batch Included"):
            with open(os.path.join(FILES_PATH, 'adult-columnar/serving.yaml')) as f:
                c = HSContract.load(f)
                df = pd.DataFrame(np.ones((12, 12), dtype="int"), columns=c.input_names)
                expected_dict = dict(zip(c.input_names, np.ones((12, 12, 1), dtype="int")))
                constructed_dict = c.make_input_dict(df, {})
                self.assertTrue(c.verify_input_dict(expected_dict)[0])
                self.assertTrue(c.verify_input_dict(constructed_dict)[0])
                for tensor_name in c.input_names:
                    np.testing.assert_array_equal(expected_dict[tensor_name], constructed_dict[tensor_name])

    def test_batch_df_to_scalar(self):
        with open(os.path.join(FILES_PATH, 'adult-scalar/serving.yaml')) as f:
            c = HSContract.load(f)
            df = pd.DataFrame(np.ones((2, 12), dtype="int"), columns=c.input_names)
            constructed_dict = c.make_input_dict(df, {})
            self.assertFalse(c.verify_input_dict(constructed_dict)[0])

    def test_permuted_dims_tensor_contract(self):
        with open(os.path.join(FILES_PATH, 'adult-tensor/serving.yaml')) as f:
            c = HSContract.load(f)
            df = pd.DataFrame(np.ones((12, 1), dtype="int"))
            constructed_dict = c.make_input_dict(df, {})
            self.assertFalse(c.verify_input_dict(constructed_dict)[0])

    def test_kwargs_scalar_input(self):
        with open(os.path.join(FILES_PATH, 'adult-scalar/serving.yaml')) as f:
            c = HSContract.load(f)
            expected_dict = dict(zip(c.input_names, np.ones(12, dtype="int")), )
            constructed_dict = c.make_input_dict(None, dict(zip(c.input_names, np.ones(12, dtype="int"))))
            self.assertEqual(expected_dict, constructed_dict)
