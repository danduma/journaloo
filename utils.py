import torch.cuda


def get_compute_device():
    if torch.cuda.is_available():
        return 'cuda'
    elif torch.has_mps:
        return 'mps'
    else:
        return 'cpu'
