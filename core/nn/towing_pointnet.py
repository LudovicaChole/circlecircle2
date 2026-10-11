"""Small PointNet-style classifier: shared point MLP and symmetric max pooling."""
from pathlib import Path
import os
import tempfile
import numpy as np
import torch
from torch import nn
from core.nn.towing_data import normalize
from utilities.towing_settings import model_path


class TowingPointNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.points = nn.Sequential(nn.Conv1d(6, 32, 1), nn.ReLU(),
                                    nn.Conv1d(32, 64, 1), nn.ReLU(),
                                    nn.Conv1d(64, 128, 1), nn.ReLU())
        self.head = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 2))

    def forward(self, xyz):
        features = torch.cat((xyz, xyz.norm(dim=2,keepdim=True),
                              xyz[:,:,1:].norm(dim=2,keepdim=True),xyz[:,:,:1].abs()),dim=2)
        return self.head(self.points(features.transpose(1, 2)).amax(dim=2))


def train(parts, labels, kind, epochs=100, progress=lambda text: None, cancelled=lambda: False,
          destination=None, learning_rate=.001, batch_size=8):
    if len(parts) != len(labels) or set(labels) != {0, 1}:
        raise ValueError('Select target parts AND background parts. Both classes are required.')
    if epochs < 1:
        raise ValueError('Epochs must be positive.')
    if not np.isfinite(learning_rate) or not 0 < learning_rate <= 1 or type(batch_size) is not int or batch_size < 1:
        raise ValueError('Invalid learning rate or batch size.')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    progress(f'Training {kind} on {device}: {sum(labels)} targets, {len(labels)-sum(labels)} backgrounds')
    model = TowingPointNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    counts = np.bincount(labels, minlength=2)
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(1/counts, dtype=torch.float32, device=device))
    rng = np.random.default_rng(20261007)
    clouds_cache = []
    for part in parts:
        if cancelled():
            raise InterruptedError('Training cancelled; previous model was preserved.')
        clouds_cache.append(normalize(part.points, count=min(len(part.points), 4096)))
    for epoch in range(epochs):
        if cancelled():
            raise InterruptedError('Training cancelled; previous model was preserved.')
        model.train()
        total = 0.0
        order = rng.permutation(len(parts))
        for start in range(0, len(order), batch_size):
            if cancelled():
                raise InterruptedError('Training cancelled; previous model was preserved.')
            indices = order[start:start+batch_size]
            clouds = []
            for index in indices:
                cached = clouds_cache[index]
                cloud = cached[rng.choice(len(cached), 512, replace=len(cached) < 512)]
                # Resolve PCA sign ambiguity through augmentation; retain principal axes.
                signs = rng.choice([-1,1],3)
                signs[2] = signs[0]*signs[1]
                clouds.append((cloud*signs+rng.normal(0,.002,cloud.shape)).astype(np.float32))
            x = torch.from_numpy(np.stack(clouds)).to(device)
            y = torch.tensor([labels[i] for i in indices], device=device)
            optimizer.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            optimizer.step()
            total += loss.item()
        if epoch == 0 or (epoch+1) % 5 == 0 or epoch+1 == epochs:
            progress(f'Epoch {epoch+1}/{epochs}, training loss {total:.5f}')
    # No claim of validation accuracy: rotated copies are not independent test files.
    target = Path(destination) if destination else model_path(kind)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=target.parent, suffix='.pt')
    os.close(fd)
    try:
        torch.save({'schema': 2, 'kind': kind, 'architecture': 'pointnet-small-pca6',
                    'state_dict': {k: v.cpu() for k, v in model.state_dict().items()},
                    'samples': [{'source': p.source, 'pid': p.pid, 'label': int(label)}
                                for p, label in zip(parts, labels)],
                    'threshold': .9, 'epochs': epochs,
                    'learning_rate': learning_rate, 'batch_size': batch_size}, temporary)
        if cancelled():
            raise InterruptedError('Training cancelled; previous model was preserved.')
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    progress(f'Model saved: {target}. Validate it on separate files before engineering use.')
    return target


def validate(parts, kind, path=None, progress=lambda text: None, cancelled=lambda: False,
             minimum_precision=.9, minimum_recall=.9):
    if not parts or {p.target for p in parts} != {False, True}:
        raise ValueError('Validation requires labeled target and background parts.')
    if not all(np.isfinite(v) and 0 <= v <= 1 for v in (minimum_precision, minimum_recall)):
        raise ValueError('Validation acceptance criteria must be between 0 and 1.')
    predictor = Predictor(kind, path)
    overlap = [p.source for p in parts if os.path.normcase(str(Path(p.source).resolve())) in predictor.training_sources]
    if overlap:
        raise ValueError('Validation folder contains training files. Select separate files.')
    tp = tn = fp = fn = 0
    for index, part in enumerate(parts, 1):
        if cancelled():
            raise InterruptedError('Validation cancelled.')
        probability = predictor.probability(part.points)
        predicted = probability >= predictor.threshold
        tp += int(predicted and part.target)
        tn += int(not predicted and not part.target)
        fp += int(predicted and not part.target)
        fn += int(not predicted and part.target)
        progress(f'Validation {index}/{len(parts)}: PART {part.pid}, target probability {probability:.3f}')
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    passed = tp > 0 and precision >= minimum_precision and recall >= minimum_recall
    return (f'{"PASS" if passed else "FAIL"} against selected criteria '
            f'(precision >= {minimum_precision:.1%}, recall >= {minimum_recall:.1%}). '
            f'Validation accuracy: {(tp+tn)/len(parts):.1%}; precision: {precision:.1%}; '
            f'recall: {recall:.1%}. TP={tp}, TN={tn}, FP={fp}, FN={fn}. '
            'This evaluates the selected validation set only.')


class Predictor:
    def __init__(self, kind, path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        record = torch.load(path or model_path(kind), map_location='cpu', weights_only=True)
        if record.get('schema') != 2 or record.get('kind') != kind or record.get('architecture') != 'pointnet-small-pca6':
            raise ValueError('Incompatible towing neural-network model.')
        self.threshold = float(record['threshold'])
        self.training_sources = {os.path.normcase(str(Path(s['source']).resolve())) for s in record.get('samples', [])}
        if not .5 <= self.threshold < 1:
            raise ValueError('Invalid towing model confidence threshold.')
        self.model = TowingPointNet().to(self.device)
        self.model.load_state_dict(record['state_dict'])
        self.model.eval()

    def probability(self, points):
        # Vote over fixed rotations so inference is repeatable and less orientation-sensitive.
        cloud = normalize(points)
        rotations = (np.eye(3), np.diag([-1,1,-1]),
                     np.diag([-1,-1,1]), np.diag([1,-1,-1]))
        x = torch.from_numpy(np.stack([cloud @ r for r in rotations]).astype(np.float32)).to(self.device)
        with torch.inference_mode():
            return float(self.model(x).softmax(dim=1)[:, 1].mean().cpu())
