import unittest

from hydro_serving_grpc import TensorShapeProto

from hydroserving.helpers.contract import shape_to_proto


class ContractHelperTests(unittest.TestCase):

    def test_empty_shape_to_proto(self):
        shape = None
        result = shape_to_proto(shape)
        assert result is None

    def test_scalar_shape_to_proto(self):
        shape = []
        result = shape_to_proto(shape)
        expected = TensorShapeProto(dim=[])
        assert result == expected

    def test_list_shape_to_proto(self):
        shape = [-1, 2, 3, 4]
        result = shape_to_proto(shape)
        expected = TensorShapeProto(dim=[
            TensorShapeProto.Dim(size=-1),
            TensorShapeProto.Dim(size=2),
            TensorShapeProto.Dim(size=3),
            TensorShapeProto.Dim(size=4)
        ])
        assert result == expected

    def test_incorrect_shape_to_proto(self):
        with self.assertRaises(ValueError) as ex:
            shape_to_proto({})
