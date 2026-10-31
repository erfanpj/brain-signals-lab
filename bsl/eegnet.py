"""EEGNet-style model (after Lawhern et al., 2018) and a CPU-budgeted training loop. Uses torch (CPU)."""
import time

import numpy as np
import torch
from torch import nn


class BudgetExceeded(RuntimeError):
    pass


class EEGNet(nn.Module):
    def __init__(self, n_ch=64, n_t=240, dropout=0.25, F1=8, D=2, F2=16, k1=40, k2=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, F1, (1, k1), padding=(0, k1 // 2), bias=False), nn.BatchNorm2d(F1),
            nn.Conv2d(F1, F1 * D, (n_ch, 1), groups=F1, bias=False), nn.BatchNorm2d(F1 * D), nn.ELU(),
            nn.AvgPool2d((1, 4)), nn.Dropout(dropout),
            nn.Conv2d(F1 * D, F1 * D, (1, k2), padding=(0, k2 // 2), groups=F1 * D, bias=False),
            nn.Conv2d(F1 * D, F2, 1, bias=False), nn.BatchNorm2d(F2), nn.ELU(),
            nn.AvgPool2d((1, 8)), nn.Dropout(dropout), nn.Flatten())
        with torch.no_grad():
            n_feat = self.net(torch.zeros(1, 1, n_ch, n_t)).shape[1]
        self.fc = nn.Linear(n_feat, 2)

    def forward(self, x):
        return self.fc(self.net(x.unsqueeze(1)))


def seed_all(seed):
    torch.manual_seed(seed); np.random.seed(seed)
    torch.use_deterministic_algorithms(True)


def train(X, y, dropout, epochs, seed, X_val=None, y_val=None, cpu_deadline=None, batch=64):
    """Train for `epochs`; if validation data is given, return accuracy after every epoch.
    Raises BudgetExceeded as soon as process CPU time passes cpu_deadline (seconds)."""
    seed_all(seed)
    model = EEGNet(n_ch=X.shape[1], n_t=X.shape[2], dropout=dropout)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    Xt, yt = torch.from_numpy(X), torch.from_numpy(y.astype(np.int64))
    gen = torch.Generator().manual_seed(seed)
    val_acc = []
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(len(Xt), generator=gen)
        for i in range(0, len(perm), batch):
            b = perm[i:i + batch]
            opt.zero_grad(); nn.functional.cross_entropy(model(Xt[b]), yt[b]).backward(); opt.step()
        if X_val is not None:
            val_acc.append(float((predict(model, X_val) == y_val).mean()))
        if cpu_deadline is not None and time.process_time() > cpu_deadline:
            raise BudgetExceeded(f"process CPU {time.process_time():.0f}s > {cpu_deadline:.0f}s")
    return model, val_acc


def predict(model, X):
    model.eval()
    with torch.no_grad():
        return np.concatenate([model(torch.from_numpy(X[i:i + 256])).argmax(1).numpy() for i in range(0, len(X), 256)])
