import numpy as np
import pytest

torch = pytest.importorskip("torch")


def test_eegnet_shapes_and_deterministic():
    from bsl.eegnet import EEGNet, predict, train
    rng = np.random.default_rng(0)
    X = rng.standard_normal((40, 64, 240)).astype(np.float32); y = rng.integers(0, 2, 40)
    assert EEGNet()(torch.from_numpy(X[:3])).shape == (3, 2)
    m1, v1 = train(X, y, 0.25, 2, 1, X, y); m2, v2 = train(X, y, 0.25, 2, 1, X, y)
    assert v1 == v2 and (predict(m1, X) == predict(m2, X)).all()


def test_budget_abort():
    from bsl.eegnet import BudgetExceeded, train
    X = np.zeros((8, 64, 240), np.float32); y = np.array([0, 1] * 4)
    with pytest.raises(BudgetExceeded):
        train(X, y, 0.25, 1, 0, cpu_deadline=0.0)
