import unittest

from hydro_serving_grpc import TensorShapeProto, DT_INT8, ModelField, DT_DOUBLE, DT_UINT32, DT_FLOAT

from hydroserving.helpers.contract import shape_to_proto, field_from_dict


class ContractHelperTests(unittest.TestCase):

    def test_empty_shape_to_proto(self):
        shape = None
        result = shape_to_proto(shape)
        self.assertIsNone(result)

    def test_scalar_shape_to_proto(self):
        shape = []
        result = shape_to_proto(shape)
        expected = TensorShapeProto(dim=[])
        self.assertEqual(result, expected)

    def test_list_shape_to_proto(self):
        shape = [-1, 2, 3, 4]
        result = shape_to_proto(shape)
        expected = TensorShapeProto(dim=[
            TensorShapeProto.Dim(size=-1),
            TensorShapeProto.Dim(size=2),
            TensorShapeProto.Dim(size=3),
            TensorShapeProto.Dim(size=4)
        ])
        self.assertEqual(result, expected)

    def test_incorrect_shape_to_proto(self):
        with self.assertRaises(ValueError) as ex:
            shape_to_proto({})

    def test_simple_field_to_proto(self):
        field_name = "test_field"
        field_dict = {
            "shape": "scalar",
            "type": "int8",
            "profile": "cool"
        }
        result = field_from_dict(field_name, field_dict)
        expected = ModelField(
            name="test_field",
            shape=TensorShapeProto(),
            dtype=DT_INT8
        )
        self.assertEqual(result, expected)

    def test_map_field_to_proto(self):
        field_name = "test_field"
        field_dict = {
            "shape": [-1],
            "profile": "cool",
            "fields": {
                "subfield1": {
                    "shape": [-1, 5],
                    "type": "float32"
                },
                "subfield2": {
                    "shape": [-1, 2],
                    "type": "uint32"
                }
            }
        }
        result = field_from_dict(field_name, field_dict)
        expected = ModelField(
            name="test_field",
            shape=TensorShapeProto(dim=[TensorShapeProto.Dim(size=-1)]),
            subfields=ModelField.Subfield(data=[
                ModelField(
                    name="subfield1",
                    shape=TensorShapeProto(dim=[
                        TensorShapeProto.Dim(size=-1),
                        TensorShapeProto.Dim(size=5)
                    ]),
                    dtype=DT_FLOAT
                ),
                ModelField(
                    name="subfield2",
                    shape=TensorShapeProto(dim=[
                        TensorShapeProto.Dim(size=-1),
                        TensorShapeProto.Dim(size=2)
                    ]),
                    dtype=DT_UINT32
                )
            ])
        )
        self.assertEqual(result.name, expected.name)
        self.assertEqual(result.shape, expected.shape)

        res_sub_len = len(result.subfields.data)
        exp_sub_len = len(expected.subfields.data)
        self.assertEqual(res_sub_len, exp_sub_len)