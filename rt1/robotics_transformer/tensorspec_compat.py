"""TF2-compatible flat spec mapping used by this RT-1 checkout.

RT-1 only uses Tensor2Robot's TensorSpecStruct as an ordered, attribute-access
mapping. The old package imports tensorflow.contrib, which TF2 removed.
This adapter supports that flat mapping use only; it does not implement
Tensor2Robot's flattened slash paths, protobuf serialization or estimators.
"""
from collections import OrderedDict


class TensorSpecStruct(OrderedDict):
    """Ordered mapping with attribute access to its keys."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
