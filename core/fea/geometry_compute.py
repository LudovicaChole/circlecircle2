"""Bounded-memory float64 geometry kernels with optional CUDA acceleration.

No global torch device/thread settings are changed. A failed CUDA operation is
retried completely on CPU. Importing this module does not import PyTorch.
"""
import os
import numpy as np
from utilities.logger import logger


class GeometryCompute:
    def __init__(self, device=None, query_chunk=256, reference_chunk=4096):
        self.device = device or os.environ.get('CIRCLECIRCLE_FEA_DEVICE', 'auto').lower()
        if self.device not in ('auto', 'cpu', 'cuda'):
            raise ValueError('CIRCLECIRCLE_FEA_DEVICE must be auto, cpu or cuda')
        if query_chunk <= 0 or reference_chunk <= 0:
            raise ValueError('Geometry chunk sizes must be positive')
        self.query_chunk, self.reference_chunk = query_chunk, reference_chunk
        self.cuda_failed = False
        self.last_backend = 'cpu'
        self._reported = set()

    def _torch(self, large):
        if self.device == 'cpu' or self.cuda_failed or (self.device == 'auto' and not large):
            return None
        try:
            import torch
            return torch if torch.cuda.is_available() else None
        except (ImportError, OSError, RuntimeError):
            self.cuda_failed = True
            return None

    def _run(self, name, large, cpu, gpu):
        torch = self._torch(large)
        if torch is not None:
            try:
                with torch.inference_mode():
                    result = gpu(torch)
                self.last_backend = 'cuda'
                if (name, 'cuda') not in self._reported:
                    logger.info(f'FEA CUDA: {name} on {torch.cuda.get_device_name(0)} (float64, chunked)')
                    self._reported.add((name, 'cuda'))
                return result
            except RuntimeError as error:
                self.cuda_failed = True
                logger.warning(f'FEA CUDA unavailable for {name}; retrying on CPU: {error}')
        self.last_backend = 'cpu'
        if large and (name, 'cpu') not in self._reported:
            logger.info(f'FEA CPU: {name} (float64, vectorized)')
            self._reported.add((name, 'cpu'))
        return cpu()

    @staticmethod
    def _points(values):
        result = np.asarray(values, dtype=np.float64).reshape(-1, 3)
        if not np.isfinite(result).all():
            raise ValueError('Geometry coordinates must be finite')
        return result

    def nearest(self, queries, references):
        q, r = self._points(queries), self._points(references)
        if not len(r):
            raise ValueError('Nearest-face search has no reference points')
        if not len(q):
            return np.empty(0, dtype=np.int64)

        def calculate(torch=None):
            output = np.empty(len(q), dtype=np.int64)
            for start in range(0, len(q), self.query_chunk):
                points = q[start:start+self.query_chunk]
                if torch is not None:
                    points = torch.as_tensor(points, device='cuda', dtype=torch.float64)
                    best = torch.full((len(points),), float('inf'), device='cuda', dtype=torch.float64)
                    indices = torch.zeros(len(points), device='cuda', dtype=torch.int64)
                else:
                    best = np.full(len(points), np.inf)
                    indices = np.zeros(len(points), dtype=np.int64)
                for offset in range(0, len(r), self.reference_chunk):
                    refs = r[offset:offset+self.reference_chunk]
                    if torch is not None:
                        refs = torch.as_tensor(refs, device='cuda', dtype=torch.float64)
                    # Direct differences avoid cancellation for models far from
                    # the origin. No float32/TF32 distance matrix multiplication.
                    distances = (points[:, None, 0] - refs[None, :, 0]) ** 2
                    for axis in (1, 2):
                        distances += (points[:, None, axis] - refs[None, :, axis]) ** 2
                    if torch is not None:
                        values, local = distances.min(dim=1)
                        improve = values < best
                        indices = torch.where(improve, local + offset, indices)
                        best = torch.minimum(best, values)
                    else:
                        local = distances.argmin(axis=1)
                        values = distances[np.arange(len(points)), local]
                        improve = values < best
                        indices[improve] = local[improve] + offset
                        best = np.minimum(best, values)
                output[start:start+len(points)] = indices.cpu().numpy() if torch is not None else indices
            return output

        # Strict '<' across chunks preserves the original first-face tie rule.
        return self._run('nearest contact faces', len(q)*len(r) >= 1_000_000,
                         calculate, lambda torch: calculate(torch))

    def velocities(self, points, center, translation, omega):
        points = self._points(points)
        center, translation, omega = (self._points([v])[0] for v in (center, translation, omega))
        def cpu():
            return translation + np.cross(omega, points-center)
        def gpu(torch):
            result = np.empty_like(points)
            c, t, w = (torch.as_tensor(v, dtype=torch.float64, device='cuda') for v in (center,translation,omega))
            for start in range(0,len(points),65536):
                p = torch.as_tensor(points[start:start+65536], dtype=torch.float64, device='cuda')
                result[start:start+len(p)] = (t + torch.linalg.cross(w.expand_as(p), p-c)).cpu().numpy()
            return result
        return self._run('initial rotational velocities', len(points) >= 32768, cpu, gpu)
